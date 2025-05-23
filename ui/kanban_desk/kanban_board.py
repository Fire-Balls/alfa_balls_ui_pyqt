import os
import shutil

from PyQt6.QtCore import QEvent
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt, QEvent, QMimeData, QPoint, QDateTime
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, \
    QAbstractItemView, QPushButton, QScrollArea, QApplication
from scripts.regsetup import description

from ui.kanban_desk.task.add_task_dialog import AddTaskDialog
from ui.kanban_desk.task.create_task_item import create_task_item
from ui.kanban_desk.task.task_widget import TaskWidget
from ui.utils import get_resource_path


class KanbanColumn(QListWidget):
    def __init__(self, title, board, parent=None):
        super().__init__(parent)
        self.setObjectName("kanban_column")
        # Разрешение на передвижение и отключение скрола
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedWidth(225)
        self.drag_source_column = None
        # Убрать пунктирное выделении при нажатии
        self.setFocusPolicy(Qt.NoFocus)
        # расстояние между тасками
        self.setSpacing(5)

        #фикс бага при повторном выделении
        self.board = board
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemSelectionChanged.connect(self.on_selection_changed)

        # Столбцы
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("margin-bottom: 5px; font-family: 'Arial'")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self)
        self.container = QWidget()
        self.container.setLayout(layout)

    def widget(self):
        return self.container

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusOut:
            self.clearSelection()  # Убираем выделение при потере фокуса
        return super().eventFilter(source, event)

    def on_selection_changed(self):
        self.board.clear_all_selections(except_column=self)

    def dropEvent(self, event):
        super().dropEvent(event)

        source_column = self.board.drag_source_column
        target_column = self
        project_name = self.board.project_name
        board_name = self.board.board_name

        if not source_column or not project_name or not board_name:
            return

        if source_column == target_column:
            return

        source_name = source_column.title_label.text().strip()
        target_name = target_column.title_label.text().strip()

        project = self.board.project_manager.projects.get(project_name)
        if not project:
            return

        board_tasks = project["boards"].setdefault(board_name, {})
        old_tasks = board_tasks.get(source_name, [])
        new_tasks = board_tasks.setdefault(target_name, [])

        for i in range(target_column.count()):
            item = target_column.item(i)
            task_data = item.data(Qt.UserRole)
            if not task_data:
                continue

            number = task_data["number"]

            # Удалить из source, если есть
            old_tasks = [t for t in old_tasks if t["number"] != number]
            board_tasks[source_name] = old_tasks

            # Добавить в target, если нет дубликатов
            if not any(t["number"] == number for t in new_tasks):
                new_tasks.append(task_data)

            # Пересоздать TaskWidget
            widget = TaskWidget(
                task_name=task_data["task_name"],
                description=task_data["description"],
                number=task_data["number"],
                avatar_path=task_data["avatar_path"],
                title=task_data["title"],
                tags=task_data["tags"],
                is_important=task_data.get("is_important", False),
                start_datetime=QDateTime.fromString(task_data.get("start_datetime", ""), Qt.ISODate),
                end_datetime=QDateTime.fromString(task_data.get("end_datetime", ""), Qt.ISODate),
                executor=task_data.get("executor", "")
            )
            target_column.setItemWidget(item, widget)
            item.setData(Qt.UserRole, task_data)

        self.board.project_manager.save_projects()
        print("[SAVE] Перемещение завершено и сохранено")

        self.board.drag_source_column = None

    def startDrag(self, supported_actions):
        self.board.drag_source_column = self  # запоминаем откуда
        super().startDrag(supported_actions)







class KanbanBoard(QWidget):
    def __init__(self, project_manager, board_name, project_name, parent=None):
        super().__init__()
        self.selected_board = None
        self.project_name = project_name
        self.folder_window = None
        self.board_name = board_name
        self.columns = {}
        self.project_manager = project_manager


        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("kanban_scroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Основные макеты
        self.board_container = DroppableBoardContainer(self)
        self.board_layout = self.board_container.layout()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.board_layout)
        self.scroll_area.setWidget(self.board_container)
        self.main_layout.addWidget(self.scroll_area)

        # Создание столбцов
        for name in ["To Do", "In Progress", "Done"]:
            column = KanbanColumn(name, self)
            column.setObjectName(name)
            self.columns[name] = column
            self.board_layout.addWidget(column.widget())

        self.add_column_button = QPushButton("Создать колонку")
        self.add_column_button.clicked.connect(self.show_add_column_dialog)
        self.main_layout.addWidget(self.add_column_button, alignment=Qt.AlignRight)
        # Кнопка добавления задачи
        self.add_task_button = QPushButton("Добавить задачу")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.main_layout.addWidget(self.add_task_button, alignment=Qt.AlignRight)

        self.setLayout(self.main_layout)


    def add_task(self, task_name, description, column_name, tags=None, files=None, number=None,
                 save_to_json=True, is_important=False,
                 start_datetime=None, end_datetime=None, executor=""):
        if column_name not in self.columns:
            print(f"[ERROR] Колонка '{column_name}' не найдена")
            return

        if number is None:
            number = self.project_manager.get_next_task_number(self.project_name)

        print(f"[ADD TASK] Добавление '{task_name}' в колонку '{column_name}' с номером {number}")

        # Создаем задачу с новыми параметрами
        item, widget = create_task_item(
            task_name=task_name,
            description=description,
            number=number,
            title=task_name,
            tags=tags,
            is_important=is_important,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            executor=executor
        )

        column = self.columns[column_name]
        column.addItem(item)
        column.setItemWidget(item, widget)
        saved_files = []
        if files and self.project_name:
            project_dir = self.project_manager.get_project_files_dir(self.project_name)
            task_dir = os.path.join(project_dir, task_name)
            os.makedirs(task_dir, exist_ok=True)

            for file_path in files:
                try:
                    file_name = os.path.basename(file_path)
                    dest = os.path.join(task_dir, file_name)
                    shutil.copy(file_path, dest)
                    saved_files.append(dest)
                except Exception as e:
                    print(f"Ошибка копирования файла: {e}")

        if save_to_json:
            project = self.project_manager.projects.get(self.project_name)
            if project is not None:
                board_name = self.board_name  # убедись, что он установлен в Window
                if "boards" not in project:
                    project["boards"] = {}
                if board_name not in project["boards"]:
                    project["boards"][board_name] = {}

                if column_name not in project["boards"][board_name]:
                    project["boards"][board_name][column_name] = []

                task_data = {
                    "task_name": task_name,
                    "description": description,
                    "number": number,
                    "avatar_path": get_resource_path("logo-alfabank.svg"),
                    "title": task_name,
                    "tags": tags or [],
                    "is_important": is_important,
                    "start_datetime": start_datetime.toString(Qt.ISODate) if start_datetime else None,
                    "end_datetime": end_datetime.toString(Qt.ISODate) if end_datetime else None,
                    "executor": executor,
                    "files": saved_files
                }

                project["boards"][board_name][column_name].append(task_data)
                print(f"[SAVE] Сохраняем задачу в проект '{self.project_name}' в доску '{board_name}': {task_data}")
                self.project_manager.save_projects()

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            name, description, tags, is_important, start_datetime, end_datetime, executor, files = dialog.get_data()
            if name:
                self.add_task(
                    task_name=name,
                    description=description,
                    column_name="To Do",
                    tags=tags,
                    is_important=is_important,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    executor=executor,
                    files= files
                )

    def clear_all_selections(self, except_column=None):
        for column in self.columns.values():
            if column is not except_column:
                column.clearSelection()

    def save_tasks(self):
        result = {}
        for name, column in self.columns.items():
            result[name] = []
            for i in range(column.count()):
                item = column.item(i)
                task_data = item.data(Qt.UserRole)
                if task_data:
                    result[name].append(task_data)
        return result

    def load_tasks(self, tasks_data: dict):
        """Теперь принимает данные доски (с колонками)"""
        self.clear_board()

        if not isinstance(tasks_data, dict):
            return

        for column_name, tasks in tasks_data.items():
            if column_name not in self.columns:
                self.add_column(column_name)

            for task in tasks:
                self.add_task(
                    task_name=task.get("task_name", ""),
                    description=task.get("description", ""),
                    column_name=column_name,
                    tags=task.get("tags", []),
                    number=task.get("number"),
                    is_important=task.get("is_important", False),
                    start_datetime=QDateTime.fromString(task["start_datetime"], Qt.ISODate) if task.get(
                        "start_datetime") else None,
                    end_datetime=QDateTime.fromString(task["end_datetime"], Qt.ISODate) if task.get(
                        "end_datetime") else None,
                    executor=task.get("executor", ""),
                    save_to_json=False
                )
    def clear_board(self):
        """Полностью очищает доску, включая все колонки и задачи"""
        # 1. Удаляем все задачи из всех колонок
        for column in self.columns.values():
            column.clear()  # Очищаем QListWidget

        # 2. Удаляем сами колонки
        for i in reversed(range(self.board_layout.count())):
            item = self.board_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
                self.board_layout.removeItem(item)

        # 3. Очищаем внутренние структуры
        self.columns.clear()

        # 4. Принудительное обновление UI
        self.update()
        QApplication.processEvents()


    def show_add_column_dialog(self):
        column_name, ok = QInputDialog.getText(self, "Новая колонка", "Введите название колонки:")
        if ok and column_name.strip():
            self.add_column(column_name.strip())

    def add_column(self, name: str):
        if name in self.columns:
            print(f"Колонка '{name}' уже существует")
            return

        column = KanbanColumn(name, self)
        wrapper = ColumnWrapperWidget(column)
        column.setObjectName(name)
        self.columns[name] = column
        self.board_layout.addWidget(wrapper)

        # === Добавляем колонку в JSON ===
        project_name = self.project_name
        board_name = self.board_name
        project = self.project_manager.projects.get(project_name)

        if project:
            boards = project.setdefault("boards", {})
            board = boards.setdefault(board_name, {})
            if name not in board:
                board[name] = []  # создаем пустую колонку

        self.project_manager.save_projects()
        print(f"[SAVE] Колонка '{name}' добавлена в JSON")

        # if self.project_name:
        #     project = self.project_manager.projects.setdefault(self.project_name, {})
        #     project.setdefault("tasks", {}).setdefault(name, [])
        #     self.project_manager.save_projects()

    def reorder_column_by_name(self, name: str, drop_pos: QPoint):
        column_wrapper = None
        for i in range(self.board_layout.count()):
            item = self.board_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, ColumnWrapperWidget):
                if widget.column.title_label.text() == name:
                    column_wrapper = widget
                    self.board_layout.removeWidget(widget)
                    break

        if column_wrapper:
            insert_index = self._find_insert_index(drop_pos)
            self.board_layout.insertWidget(insert_index, column_wrapper)

    def _find_insert_index(self, drop_pos: QPoint) -> int:
        for i in range(self.board_layout.count()):
            item = self.board_layout.itemAt(i)
            widget = item.widget()
            if widget:
                if drop_pos.x() < widget.x() + widget.width() // 2:
                    return i
        return self.board_layout.count()

    def set_project_name(self, project_name):
        self.project_name = project_name

    def get_all_columns(self):
        return self.findChildren(KanbanColumn)

    def set_project_and_board(self, project_name, board_name):
        """Устанавливает проект и доску, загружает задачи"""
        self.project_name = project_name
        self.board_name = board_name
        self.clear_board()

        project = self.project_manager.projects.get(project_name)
        if not project:
            return

        board_data = project.get("boards", {}).get(board_name, {})

        # Создаем колонки
        for column_name in ["To Do", "In Progress", "Done"]:
            if column_name not in self.columns:
                self.add_column(column_name)

        # Загружаем задачи
        self.load_tasks(board_data)


class ColumnWrapperWidget(QWidget):
    def __init__(self, column: KanbanColumn, parent=None):
        super().__init__(parent)
        self.drag_start_position = None
        self.column = column
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.column.widget())
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and (event.pos() - self.drag_start_position).manhattanLength() > 10:
            mime_data = QMimeData()
            mime_data.setText(self.column.title_label.text())

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos())
            drag.exec(Qt.MoveAction)




class DroppableBoardContainer(QWidget):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.setAcceptDrops(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        self.board.reorder_column_by_name(text, event.pos())
        event.acceptProposedAction()