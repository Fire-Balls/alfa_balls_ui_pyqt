from PyQt6.QtCore import QEvent
from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QVBoxLayout, QLabel, \
    QAbstractItemView, QPushButton

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
                    title=task_data["title"],
                    tags=task_data["tags"]
                )
                self.setItemWidget(item, widget)


class KanbanBoard(QWidget):
    def __init__(self, project_manager):
        super().__init__()
        self.project_name = None
        self.columns = {}
        self.project_manager = project_manager

        # Основные макеты
        self.board_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.board_layout)

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
        if not isinstance(tasks_data, dict):
            print("Неверный формат или пустой файл")
            return

        for column in self.findChildren(KanbanColumn):
            column.clear()

        for column_name, tasks in tasks_data.items():
            column = self.findChild(KanbanColumn, column_name)
            if column:
                for task in tasks:
                    title = task.get("task_name", "")
                    tags = task.get("tags", [])
                    number = task.get("number", 0)
                    self.add_task(title, column_name=column_name, tags=tags, number=number, save_to_json=False)
            else:
                print(f"Колонка '{column_name}' не найдена. Возможно, её нужно создать.")

    def clear_board(self):
        for column in self.columns.values():
            column.clear()

    def set_project_name(self, project_name):
        self.project_name = project_name