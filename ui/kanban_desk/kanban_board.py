from PyQt6.QtCore import QEvent
from PySide6.QtCore import Qt, QEvent, QMimeData, QPoint
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, \
    QAbstractItemView, QPushButton, QScrollArea
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
        project = self.board.project_manager.projects.get(project_name)

        if not source_column or not project:
            return

        source_name = source_column.title_label.text().strip()
        target_name = target_column.title_label.text().strip()

        if source_name == target_name:
            return

        # Словарь с задачами
        tasks_by_column = project.get("tasks", {})

        for i in range(target_column.count()):
            item = target_column.item(i)
            task_data = item.data(Qt.UserRole)
            if not task_data:
                continue

            # Удалить из старой колонки по номеру
            old_tasks = tasks_by_column.get(source_name, [])
            tasks_by_column[source_name] = [t for t in old_tasks if t["number"] != task_data["number"]]

            # Добавить в новую колонку, если ещё нет
            new_tasks = tasks_by_column.setdefault(target_name, [])
            if not any(t["number"] == task_data["number"] for t in new_tasks):
                new_tasks.append(task_data)

            # Восстановим виджет задачи
            if target_column.itemWidget(item) is None:
                widget = TaskWidget(
                    task_name=task_data["task_name"],
                    number=task_data["number"],
                    avatar_path=task_data["avatar_path"],
                    title=task_data["title"],
                    tags=task_data["tags"]
                )
                target_column.setItemWidget(item, widget)

        # Сохранение
        self.board.project_manager.save_projects()
        self.board.drag_source_column = None


    def startDrag(self, supported_actions):
        self.board.drag_source_column = self  # запоминаем откуда
        super().startDrag(supported_actions)




class KanbanBoard(QWidget):
    def __init__(self, project_manager):
        super().__init__()
        self.project_name = None
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
        for name in ["To Do", "In Progress", "Review", "Done"]:
            column = KanbanColumn(name, board=self)
            column.setObjectName(name)
            # column.setStyleSheet("""
            #
            #
            # """)
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

        # self.add_task("Сделать дизайн", "To Do")
        # self.add_task("Написать код", "In Progress")

    def add_task(self, task_name, column_name, tags=None, number=None, save_to_json=True):
        if column_name not in self.columns:
            print(f"[ERROR] Колонка '{column_name}' не найдена")
            return

        if number is None:
            number = self.project_manager.get_next_task_number(self.project_name)

        print(f"[ADD TASK] Добавление '{task_name}' в колонку '{column_name}' с номером {number}")
        item, widget = create_task_item(task_name, number, title=task_name, tags=tags)
        column = self.columns[column_name]
        column.addItem(item)
        column.setItemWidget(item, widget)

        if save_to_json:
            project = self.project_manager.projects.get(self.project_name)
            if project is not None:
                if "tasks" not in project:
                    project["tasks"] = {}
                if column_name not in project["tasks"]:
                    project["tasks"][column_name] = []

                task_data = {
                    "task_name": task_name,
                    "number": number,
                    "avatar_path": get_resource_path("logo-alfabank.svg"),
                    "title": task_name,
                    "tags": tags or []
                }
                project["tasks"][column_name].append(task_data)
                print(f"[SAVE] Сохраняем задачу в проект '{self.project_name}': {task_data}")
                self.project_manager.save_projects()

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            name, tags = dialog.get_data()
            if name:
                self.add_task(name, "To Do", tags)

    def clear_all_selections(self, except_column=None):
        for column in self.columns.values():
            if column is not except_column:
                column.clearSelection()

    def save_tasks(self):
        data = {}
        for name, column in self.columns.items():
            tasks = []
            for i in range(column.count()):
                item = column.item(i)
                task_data = item.data(Qt.UserRole)
                if task_data:
                    tasks.append(task_data)
            data[name] = tasks
        return data

    def load_tasks(self, tasks_data: dict):
        self.clear_board()
        if not isinstance(tasks_data, dict):
            print("Неверный формат или пустой файл")
            return

        for column_name, tasks in tasks_data.items():
            if column_name not in self.columns:
                self.add_column(column_name)

            column = self.columns.get(column_name)
            if column:
                for task in tasks:
                    title = task.get("task_name", "")
                    tags = task.get("tags", [])
                    number = task.get("number", None)
                    self.add_task(title, column_name=column_name, tags=tags, number=number, save_to_json=False)

    def clear_board(self):
        for column in self.columns.values():
            column.clear()

    def set_project_and_board(self, project_name, board_name):
        self.project_name = project_name
        self.board_name = board_name
        self.clear_board()
        self.clear_columns()

        project = self.project_manager.projects.get(project_name, {})
        boards = project.setdefault("boards", {})
        board = boards.setdefault(board_name, {})
        tasks = board.setdefault("tasks", {})

        if not tasks:
            for name in ["To Do", "In Progress", "Review", "Done"]:
                self.add_column(name)
        else:
            for column_name in tasks:
                self.add_column(column_name)

        self.load_tasks(tasks)

    def show_add_column_dialog(self):
        from PySide6.QtWidgets import QInputDialog
        column_name, ok = QInputDialog.getText(self, "Новая колонка", "Введите название колонки:")
        if ok and column_name.strip():
            self.add_column(column_name.strip())

    def add_column(self, name: str):
        if name in self.columns:
            print(f"Колонка '{name}' уже существует")
            return

        column = KanbanColumn(name, board=self)
        wrapper = ColumnWrapperWidget(column)
        column.setObjectName(name)
        self.columns[name] = column
        self.board_layout.addWidget(column.widget())

        if self.project_name:
            project = self.project_manager.projects.setdefault(self.project_name, {})
            project.setdefault("tasks", {}).setdefault(name, [])
            self.project_manager.save_projects()

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

    def clear_columns(self):
        for column in self.columns.values():
            self.board_layout.removeWidget(column.widget())
            column.widget().deleteLater()
        self.columns.clear()

    def set_project_name(self, project_name):
        self.project_name = project_name


class ColumnWrapperWidget(QWidget):
    def __init__(self, column: KanbanColumn, parent=None):
        super().__init__(parent)
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