from PyQt6.QtCore import QEvent
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QAbstractItemView
from PySide6.QtCore import Qt, QEvent

from ui.utils import get_resource_path
from ui.kanban_desk.task.task_widget import TaskWidget  # импортируй

class KanbanColumn(QListWidget):
    def __init__(self, title, board, parent=None):
        super().__init__(parent)
        self.setObjectName("kanban_column")
        # Разрешение на передвижение
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
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
        self.layout = QHBoxLayout(self)
        self.columns = {}

        for name in ["To Do", "In Progress", "Review", "Done"]:
            column = KanbanColumn(name, board=self)
            self.columns[name] = column
            self.layout.addWidget(column.widget())

        self.add_task("Сделать дизайн", "To Do")
        self.add_task("Написать код", "In Progress")

    def add_task(self, task_name, column_name):
        if column_name in self.columns:
            self.task_counter += 1
            number = self.task_counter

            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 60))

            full_task_name = f"{task_name}.{number}"
            avatar_path = get_resource_path("logo-alfabank.svg")
            tags = ["js", "C", "HTTP"]

            # Сохраняем все данные
            item.setData(Qt.UserRole, {
                "task_name": task_name,
                "number": number,
                "avatar_path": avatar_path,
                "tags": tags
            })

            # Создаем кастомный виджет
            widget = TaskWidget(task_name=task_name, number=number, avatar_path=avatar_path, tags=tags)

            self.columns[column_name].addItem(item)
            self.columns[column_name].setItemWidget(item, widget)

    def clear_all_selections(self, except_column=None):
        for column in self.columns.values():
            if column is not except_column:
                column.clearSelection()