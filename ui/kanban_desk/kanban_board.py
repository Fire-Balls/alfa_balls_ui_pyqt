import os
import shutil
import sys
# from PyQt6.QtCore import QEvent
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt, QEvent, QMimeData, QPoint, QDateTime
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, \
    QAbstractItemView, QPushButton, QScrollArea, QApplication

from network.new.models import Board, Issue, IssueShortcut, Project
from network.new.operations import ServiceOperations
from ui.kanban_desk.task.add_task_dialog import AddTaskDialog
from ui.kanban_desk.task.create_task_item import create_task_item
from ui.kanban_desk.task.task_widget import TaskWidget
from ui.utils import ProjectManager


class KanbanColumn(QListWidget):
    def __init__(self, title, board, status_id, parent=None):
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

        # фикс бага при повторном выделении
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
        project_id = self.board.project_id
        board_id = self.board.board_id

        if not source_column or not project_id or not board_id:
            return

        if source_column == target_column:
            return

        source_name = source_column.title_label.text().strip()
        target_name = target_column.title_label.text().strip()

        project = ServiceOperations.get_project(self.board.project_id)
        if not project:
            return

        board_tasks = project.boards
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

        self.board.drag_source_column = None

    def startDrag(self, supported_actions):
        self.board.drag_source_column = self  # запоминаем откуда
        super().startDrag(supported_actions)


class KanbanBoard(QWidget):
    def __init__(self, user_id, board_id):
        super().__init__()
        self.user_id = user_id
        self.board_id = board_id
        self.columns = {}

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

        self.columns = {}
        for status in ServiceOperations.get_board(0, board_id).statuses:
            column = KanbanColumn(status.name, self, status.id)
            column.setObjectName(status.name)
            self.columns[status.name] = column
            self.board_layout.addWidget(column.widget())

        self.add_column_button = QPushButton("Создать колонку")
        self.add_column_button.clicked.connect(self.show_add_column_dialog)
        self.main_layout.addWidget(self.add_column_button, alignment=Qt.AlignRight)
        # Кнопка добавления задачи
        self.add_task_button = QPushButton("Добавить задачу")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.main_layout.addWidget(self.add_task_button, alignment=Qt.AlignRight)

        self.setLayout(self.main_layout)

    def add_task(self, issue: IssueShortcut | Issue):
        if issue.status.name not in self.columns:
            print(f"[ERROR] Колонка '{issue.status.name}' не найдена")
            return

        print(f"[ADD TASK] Добавление '{issue.title}' в колонку '{issue.status}' с номером {issue.code}")

        # Создаем задачу с новыми параметрами
        item, widget = create_task_item(
            task_name=issue.title,
            description=issue.description,
            number=issue.code,
            title=issue.title,
            tags=issue.tags,
            is_important=False,
            executor=issue.assignee.full_name
        )

        column = self.columns[issue.status.name]
        column.addItem(item)
        column.setItemWidget(item, widget)

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec():
            name, description, tags, is_important, start_datetime, end_datetime, executor, files = dialog.get_data()
            if name:
                saved_task = ServiceOperations.create_new_issue(0, self.board_id, name, description,
                                                                self.user_id, self.user_id, end_datetime, tags)
                retrieved_task = ServiceOperations.get_issue(0, self.board_id, saved_task.id)
                self.add_task(retrieved_task)

    def clear_all_selections(self, except_column=None):
        for column in self.columns.values():
            if column is not except_column:
                column.clearSelection()

    def load_tasks(self, board: Board):
        """Принимает models.Board"""
        # self.clear_board() #TODO

        if not isinstance(board, Board):
            return

        for issue in board.issues:
            self.add_task(issue)

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
        #self.columns.clear()

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
        print('add_column', name)
        created_status = ServiceOperations.create_new_status(name, 0, self.board_id)

        column = KanbanColumn(created_status.name, self, created_status.id)
        wrapper = ColumnWrapperWidget(column)
        column.setObjectName(created_status.name)
        self.columns[created_status.name] = column
        self.board_layout.addWidget(wrapper)

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

    def set_project_and_board(self, project: Project, board: Board):
        """Устанавливает проект и доску, загружает задачи"""
        self.project_name = project.name
        self.board_name = board.name
        # self.clear_board()

        if not project:
            return

        board_data = board

        # Создаем колонки
        for status in board_data.statuses:
            status_name = status.name
            if status_name not in self.columns:
                self.add_column(status_name)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from network.new.client_manage import get_client

    client = get_client()
    client.login("super123@urfu.ru", "super")
    # Создаём экземпляр KanbanBoard
    # Предположим, user_id = 1, board_id = 123 (замени на реальные значения)
    kanban_board = KanbanBoard(user_id=1, board_id=1)
    kanban_board.show()

    sys.exit(app.exec_())