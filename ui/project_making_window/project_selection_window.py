from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
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
        dialog.setFixedSize(250, 220)

        layout = QVBoxLayout(dialog)
        # Название проекта
        name_label = QLabel("Введите название проекта:")
        name_input = QLineEdit()
        # Название доски
        board_label = QLabel("Введите название доски:")
        board_input = QLineEdit()
        # Код проекта и фильтры
        project_code_label = QLabel("Введите наименование кода для задач:")
        project_code_input = QLineEdit()
        project_code_input.setToolTip("Допустимые символы: <br>A-Z<br>0-9<br>Максимум 3 символа")
        project_code_input.setMaxLength(3)
        regex = QRegularExpression("[A-Z0-9]{0,3}")
        validator = QRegularExpressionValidator(regex)
        project_code_input.setValidator(validator)

        project_code_help = QLabel("Допустимые символы: <br>A-Z<br>0-9<br>Максимум 3 символа")

        warning_text = QLabel("Необходимо заполнить все строки!")
        warning_text.setObjectName("warning_text")
        warning_text.setStyleSheet("color: red;")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(board_label)
        layout.addWidget(board_input)
        layout.addWidget(project_code_label)
        layout.addWidget(project_code_input)
        #layout.addWidget(project_code_help)
        layout.addWidget(warning_text)
        layout.addWidget(button_box)

        project_code_input.textChanged.connect(self.validate_input)
        board_input.textChanged.connect(self.validate_input)
        name_input.textChanged.connect(self.validate_input)

        if dialog.exec() == QDialog.Accepted:
            name = name_input.text().strip()
            board_title = board_input.text().strip() or "Моя доска"
            project_code = project_code_input.text().strip()

            if name and name not in ServiceOperations.get_all_projects_by_user(self.user_id):
                ServiceOperations.create_new_project_with_board(name, project_code, board_title, "OWNER",
                                                                self.user_id)
                self.load_projects()
                # self.projects_list_signal.emit(ServiceOperations.get_all_projects_by_user(self.user_id))

    def validate_input(self):
        sender = self.sender()
        dialog = sender.window()  # получаем родительское окно

        # Найдём нужные виджеты
        name_input = dialog.findChild(QLineEdit, "")
        board_input = dialog.findChildren(QLineEdit)[1]
        project_code_input = dialog.findChildren(QLineEdit)[2]
        warning_label = dialog.findChild(QLabel, "warning_text")
        button_box = dialog.findChild(QDialogButtonBox)

        all_filled = all([
            name_input.text().strip(),
            board_input.text().strip(),
            project_code_input.text().strip()
        ])

        button_box.button(QDialogButtonBox.Ok).setEnabled(all_filled)
        warning_label.setText("Необходимо заполнить все строки!" if not all_filled else "")

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


