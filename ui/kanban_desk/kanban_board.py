from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class KanbanColumn(QListWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        # Разрешение на передвижение
        self.setObjectName("kanban_desk")
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSpacing(5)
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


class KanbanBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.columns = {}

        for name in ["To Do", "In Progress", "Review", "Done"]:
            column = KanbanColumn(name)
            self.columns[name] = column
            self.layout.addWidget(column.widget())

        self.add_task("Сделать дизайн", "To Do")
        self.add_task("Написать код", "In Progress")

    def add_task(self, task_name, column_name):
        if column_name in self.columns:
            item = QListWidgetItem(task_name)
            item.setData(Qt.UserRole, "kanbanTask")

            item.setSizeHint(QSize(200, 40))
            self.columns[column_name].addItem(item)