import sys
from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QIcon, QAction, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
    QFrame, QComboBox, QToolButton, QMenu, QDialog, QLabel, QLineEdit, QMessageBox
)

from ui.kanban_desk.kanban_board import KanbanBoard
from ui.profile_window import ProfileWindow
from ui.utils import get_resource_path, ProjectManager

class PlaceholderInterface(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QPushButton(f"{title} content"))

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kanban Project")
        self.resize(1000, 700)
        self.setMinimumSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet("background-color: #e0e0e0;")

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("QComboProjectsList")
        self.project_manager = ProjectManager()
        self.populate_projects()
        self.dropdown.activated.connect(self.on_project_selected)

        self.profile_button = QToolButton()
        self.profile_button.setIcon(QIcon(get_resource_path("profile_icon.svg")))
        self.profile_button.setIconSize(QSize(36, 36))
        self.profile_button.setObjectName("profile_button")
        self.profile_button.setFocusPolicy(Qt.NoFocus)
        self.profile_button.setPopupMode(QToolButton.InstantPopup)

        self.profile_window = None
        profile_menu = RoundedMenu(self, radius=16)
        profile_action = QAction("Профиль", self)
        profile_action.triggered.connect(self.open_profile_window)
        profile_menu.addAction(profile_action)
        profile_menu.addAction(QAction("Настройки", self))
        profile_menu.addSeparator()
        profile_menu.addAction(QAction("Выход", self))
        profile_menu.aboutToShow.connect(self.show_profile_border)
        profile_menu.aboutToHide.connect(self.hide_profile_border)
        self.profile_button.setMenu(profile_menu)

        top_layout.addWidget(self.dropdown)
        top_layout.addStretch()
        top_layout.addWidget(self.profile_button)
        main_layout.addWidget(self.top_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.menu = QListWidget()
        self.menu.setObjectName("side_menu")
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setFixedWidth(43)
        self.menu.setIconSize(QSize(24, 24))
        self.menu.setSpacing(7)


        alfa_item = QListWidgetItem(QIcon(get_resource_path("logo-alfabank.svg")), "")
        alfa_item.setFlags(Qt.NoItemFlags)
        alfa_item.setData(Qt.UserRole, "noHover")
        self.menu.addItem(alfa_item)

        menu_item = QListWidgetItem(QIcon(get_resource_path("menu_icon.svg")), "")
        menu_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(menu_item)

        file_item = QListWidgetItem(QIcon(get_resource_path("file_icon.svg")), "")
        file_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(file_item)

        gear_item = QListWidgetItem(QIcon(get_resource_path("gear_icon.svg")), "")
        gear_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(gear_item)

        self.stack = QStackedWidget()
        self.board = KanbanBoard()
        self.stack.addWidget(self.board)
        self.folder = PlaceholderInterface("Folder")
        self.settings = PlaceholderInterface("Settings")

        self.stack.addWidget(self.folder)
        self.stack.addWidget(self.settings)

        self.menu.currentRowChanged.connect(self.on_menu_changed)
        self.menu.setCurrentRow(1)

        content_layout.addWidget(self.menu)
        content_layout.addWidget(self.stack)

        main_layout.addLayout(content_layout)

        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))

    def on_menu_changed(self, index):
        if index > 0:
            self.stack.setCurrentIndex(index - 1)

    def show_profile_border(self):
        self.profile_button.setStyleSheet("""
            QToolButton#profile_button {
                border: 2px solid #ee3424;
                border-radius: 16px;
            }
        """)

    def hide_profile_border(self):
        self.profile_button.setStyleSheet("""
            QToolButton#profile_button {
                border: none;
                border-radius: 16px;
            }
        """)

    def open_profile_window(self):
        if self.profile_window is None:
            self.profile_window = ProfileWindow(self.profile_button)
        self.profile_window.show()
        self.profile_window.raise_()
        self.profile_window.activateWindow()

    def populate_projects(self):
        self.dropdown.clear()
        self.dropdown.addItems(self.project_manager.get_projects())
        self.dropdown.addItem("➕ Добавить проект")

    def on_project_selected(self, index):
        if self.dropdown.itemText(index) == "➕ Добавить проект":
            current_index = self.dropdown.currentIndex()
            dialog = AddProjectDialog(self, self.project_manager)
            if dialog.exec():
                project_name = dialog.get_project_name()
                if project_name:
                    self.project_manager.add_project(project_name)
                    self.populate_projects()
                    project_index = self.dropdown.findText(project_name)
                    if project_index != -1:
                        self.dropdown.setCurrentIndex(project_index)
            else:
                # Если закрыли окно без добавления проекта, вернуть прошлый выбранный проект
                self.dropdown.setCurrentIndex(current_index)
        else:
            selected_project = self.dropdown.currentText()
            print(f"Открываем проект: {selected_project}")

class RoundedMenu(QMenu):
    def __init__(self, parent=None, radius=10):
        super().__init__(parent)
        self.radius = radius
        self.setObjectName("profile_menu")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def showEvent(self, event):
        super().showEvent(event)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

class AddProjectDialog(QDialog):
    def __init__(self, parent=None, project_manager=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setWindowTitle("Добавить проект")
        self.setFixedSize(300, 160)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Введите название проекта:")
        self.layout.addWidget(self.label)
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.layout.addWidget(self.error_label)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.validate_and_accept)
        self.layout.addWidget(self.add_button)

    def get_project_name(self):
        return self.name_input.text().strip()

    def validate_and_accept(self):
        name = self.get_project_name()
        if not name:
            self.error_label.setText("Название проекта не может быть пустым.")
            return
        if self.project_manager and name in self.project_manager.get_projects():
            self.error_label.setText("Проект с таким названием уже существует.")
            return
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())