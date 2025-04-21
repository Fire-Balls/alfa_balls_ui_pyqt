import sys


from PySide6.QtCore import Qt, QSize, QUrl, QRect, QTimer, QRectF
from PySide6.QtGui import QIcon, QDesktopServices, QPixmap, QAction, QPainterPath, QRegion, QPainter
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
    QFrame, QLineEdit, QTableWidget, QHeaderView, QTableWidgetItem, QLabel, QComboBox, QToolButton, QMenu
)
from ui.utils import get_resource_path
from ui.profile_window import ProfileWindow


class HomeInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.kanban_table = QTableWidget(self)
        self.init_ui()


    def init_ui(self):
        self.kanban_table.setColumnCount(4)
        self.kanban_table.setHorizontalHeaderLabels(["To Do", "In Progress", "Review", "Done"])
        self.kanban_table.setRowCount(0)
        self.kanban_table.verticalHeader().setVisible(False)
        self.kanban_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.add_task("Сделать UI", "To Do")
        self.add_task("Проверить код", "In Progress")

        layout = QVBoxLayout(self)
        layout.addWidget(self.kanban_table)

    def add_task(self, task_name, column):
        row_position = self.kanban_table.rowCount()
        self.kanban_table.insertRow(row_position)
        column_index = self.get_column_index(column)
        self.kanban_table.setItem(row_position, column_index, QTableWidgetItem(task_name))

    def get_column_index(self, column_name):
        header = self.kanban_table.horizontalHeader()
        model = self.kanban_table.model()
        for i in range(header.count()):
            if model.headerData(i, Qt.Horizontal, Qt.DisplayRole) == column_name:
                return i
        return 0


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

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet("background-color: #e0e0e0;")

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)
        # Список проектов выпадающий список
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Проект A", "Проект B", "Проект C"])

        # Кнопка с круглым изображением профиля
        self.profile_button = QToolButton()
        self.profile_button.setIcon(QIcon(get_resource_path("profile_icon.svg")))
        self.profile_button.setIconSize(QSize(36, 36))
        self.profile_button.setObjectName("profile_button")
        self.profile_button.setFocusPolicy(Qt.NoFocus)
        self.profile_button.setPopupMode(QToolButton.InstantPopup)

        # Контекстное меню
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

        # Горизонтальная часть: боковое меню и основной контент
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Боковое меню
        self.menu = QListWidget()
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setFixedWidth(43)
        self.menu.setIconSize(QSize(24, 24))
        self.menu.setSpacing(7)

        icon_path_alfa = get_resource_path("logo-alfabank.svg")
        icon_path_menu = get_resource_path("menu_icon.svg")
        icon_path_file = get_resource_path("file_icon.svg")
        icon_path_gear = get_resource_path("gear_icon.svg")

        alfa_item = QListWidgetItem(QIcon(icon_path_alfa), "")
        alfa_item.setFlags(Qt.NoItemFlags)
        alfa_item.setData(Qt.UserRole, "noHover")
        self.menu.addItem(alfa_item)

        menu_item = QListWidgetItem(QIcon(icon_path_menu), "")
        menu_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(menu_item)

        file_item = QListWidgetItem(QIcon(icon_path_file), "")
        file_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(file_item)

        gear_item = QListWidgetItem(QIcon(icon_path_gear), "")
        gear_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(gear_item)

        # Контент
        self.stack = QStackedWidget()
        self.home = HomeInterface()
        self.folder = PlaceholderInterface("Folder")
        self.settings = PlaceholderInterface("Settings")

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.folder)
        self.stack.addWidget(self.settings)

        self.menu.currentRowChanged.connect(self.on_menu_changed)
        self.menu.setCurrentRow(1)

        content_layout.addWidget(self.menu)
        content_layout.addWidget(self.stack)

        main_layout.addLayout(content_layout)

        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))
    #Смена стартового меню в главном окне
    def on_menu_changed(self, index):
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
    #При нажатии показывается красная рамка
    def show_profile_border(self):
        self.profile_button.setStyleSheet("""
            QToolButton#profile_button {
                border: 2px solid #ee3424;
                border-radius: 16px;
            }
        """)
    #При выходе из меню убирается красная рамка
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


class RoundedMenu(QMenu):
    def __init__(self, parent=None, radius=10):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

    def showEvent(self, event):
        super().showEvent(event)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())