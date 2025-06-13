from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, \
    QMessageBox, QDialog, QLineEdit, QDialogButtonBox

from network.new.operations import ServiceOperations
from ui.main_window import Window
from ui.utils import get_resource_path, ProjectManager


class ProjectSelectionWindow(QWidget):
    projects_list_signal = Signal(list)

    def __init__(self, project_manager: ProjectManager, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.selected_project = None
        self.delete_button = None
        self.window = None
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

        self.delete_button = QPushButton("Удалить проект")
        self.delete_button.clicked.connect(self.delete_project)

        self.open_button = QPushButton("Открыть проект")
        self.open_button.clicked.connect(self.open_selected_project)

        # Горизонтальный layout для нижних кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.delete_button, alignment=Qt.AlignLeft)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.open_button, alignment=Qt.AlignRight)
        self.main_layout.addStretch(15)
        self.main_layout.addLayout(buttons_layout)

    def load_projects(self):
        self.project_list.clear()
        try:
            projects = ServiceOperations.get_all_projects_by_user(self.user_id)
            for p in projects:
                self.add_project_item(p.name)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проекты: {e}")

    def add_project_item(self, project_name):
        item = QListWidgetItem(project_name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.project_list.addItem(item)

    def create_new_project(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Создание проекта")

        layout = QVBoxLayout(dialog)

        name_label = QLabel("Введите название проекта:")
        name_input = QLineEdit()

        board_label = QLabel("Введите название доски:")
        board_input = QLineEdit()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addSpacing(10)
        layout.addWidget(board_label)
        layout.addWidget(board_input)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            board_title = board_input.text().strip() or "Моя доска"

            if name and name not in ServiceOperations.get_all_projects_by_user(self.user_id):
                ServiceOperations.create_new_project_with_board(name, board_title, "OWNER",
                                                                self.user_id)  # todo ввести код проекта
                self.load_projects()
                # self.projects_list_signal.emit(ServiceOperations.get_all_projects_by_user(self.user_id))

    def open_selected_project(self):
        item = self.project_list.currentItem()
        if item:
            project_name = item.text()
            self.open_project(project_name)

    def open_project(self, project_name):
        print(f"Открываем проект: {project_name}")
        selected_project = ServiceOperations.get_project_by_name(project_name, self.user_id)
        full_selected_project = ServiceOperations.get_project(selected_project.id)
        first_board = full_selected_project.boards[0]

        if first_board:
            self.window = Window(selected_project=project_name, user_id=self.user_id,
                                 project_id=selected_project.id,
                                 board_id=first_board.id)  # <- передаем выбранный проект
            self.window.show()
            self.close()

    def delete_project(self):
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Удаление проекта", "Сначала выберите проект.")
            return

        project_name = selected_items[0].text()
        confirm = QMessageBox.question(
            self, "Подтвердите удаление",
            f"Вы уверены, что хотите удалить проект «{project_name}»?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            ServiceOperations.delete_project(ServiceOperations.get_project_by_name(project_name, self.user_id).id)
            self.load_projects()
