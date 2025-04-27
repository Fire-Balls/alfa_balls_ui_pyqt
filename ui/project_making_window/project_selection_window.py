from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QInputDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, Signal

from ui.utils import get_resource_path
from ui.main_window import Window

class ProjectSelectionWindow(QWidget):
    projects_list_signal = Signal(list)

    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.board = None
        self.open_button = None
        self.project_list = None
        self.add_project_button = None
        self.main_layout = None
        self.project_manager = project_manager

        self.setWindowTitle("Выбор проекта")
        self.setFixedSize(400, 300)
        self.setObjectName("projectSelectionWindow")
        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))

        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        title = QLabel("Ваши проекты")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        self.add_project_button = QPushButton()
        self.add_project_button.setIcon(QIcon(get_resource_path("plus_icon.svg")))
        self.add_project_button.setIconSize(QSize(60, 60))
        self.add_project_button.setFixedSize(36, 36)
        self.add_project_button.setObjectName("addProjectButton")
        self.add_project_button.clicked.connect(self.create_new_project)
        top_layout.addWidget(self.add_project_button)

        self.main_layout.addLayout(top_layout)

        self.project_list = QListWidget()
        self.project_list.setObjectName("projectsList")
        self.project_list.setEditTriggers(QListWidget.NoEditTriggers)
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)
        self.main_layout.addWidget(self.project_list)

        self.open_button = QPushButton("Открыть проект")
        self.open_button.clicked.connect(self.open_selected_project)
        self.main_layout.addWidget(self.open_button, alignment=Qt.AlignRight)

    def load_projects(self):
        self.project_list.clear()
        for project in self.project_manager.get_projects():
            self.add_project_item(project)

    def add_project_item(self, project_name):
        item = QListWidgetItem(project_name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.project_list.addItem(item)

    def create_new_project(self):
        name, ok = QInputDialog.getText(self, "Создание проекта", "Введите название проекта:")
        if ok and name.strip():
            if name in self.project_manager.get_projects():
                return
            self.project_manager.add_project(name)
            self.add_project_item(name)
            self.projects_list_signal.emit(self.project_manager.get_projects())

    def open_selected_project(self):
        item = self.project_list.currentItem()
        if item:
            project_name = item.text()
            self.open_project(project_name)

    def open_project(self, project_name):
        print(f"Открываем проект: {project_name}")
        self.board = Window()
        self.board.show()
        self.close()