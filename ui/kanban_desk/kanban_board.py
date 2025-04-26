from PyQt6.QtCore import QEvent
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, \
    QAbstractItemView, QLineEdit, QComboBox, QPushButton
from PySide6.QtCore import Qt, QEvent

from ui.kanban_desk.task.create_task_item import create_task_item
from ui.kanban_desk.task.add_task_dialog import AddTaskDialog
from ui.kanban_desk.task.task_widget import TaskWidget  # импортируй

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

        for i in range(self.count()):
            item = self.item(i)

            if self.itemWidget(item) is not None:
                continue

            task_data = item.data(Qt.UserRole)
            if task_data:
                widget = TaskWidget(
                    task_name=task_data["task_name"],
                    number=task_data["number"],
                    avatar_path=task_data["avatar_path"],
                    tags=task_data["tags"]
                )
                self.setItemWidget(item, widget)


class KanbanBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_counter = 0
        self.columns = {}

        # Основные макеты
        self.board_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.board_layout)

        # Создание столбцов
        for name in ["To Do", "In Progress", "Review", "Done"]:
            column = KanbanColumn(name, board=self)
            self.columns[name] = column
            self.board_layout.addWidget(column.widget())

        # Кнопка добавления задачи
        self.add_task_button = QPushButton("Добавить задачу")
        self.add_task_button.clicked.connect(self.show_add_task_dialog)
        self.main_layout.addWidget(self.add_task_button, alignment=Qt.AlignRight)

        self.setLayout(self.main_layout)

        # self.add_task("Сделать дизайн", "To Do")
        # self.add_task("Написать код", "In Progress")

    def add_task(self, task_name, column_name, tags=None):
        if column_name in self.columns:
            self.task_counter += 1
            item, widget = create_task_item(task_name, self.task_counter, tags)
            column = self.columns[column_name]
            column.addItem(item)
            column.setItemWidget(item, widget)

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