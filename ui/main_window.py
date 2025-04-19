import sys
import os
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
    QFrame, QLineEdit, QTableWidget, QHeaderView, QTableWidgetItem, QLabel
)


class HomeInterface(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_input = QLineEdit(self)
        self.kanban_table = QTableWidget(self)
        self.init_ui()

    def init_ui(self):
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.setFixedWidth(100)

        self.kanban_table.setColumnCount(4)
        self.kanban_table.setHorizontalHeaderLabels(["To Do", "In Progress", "Review", "Done"])
        self.kanban_table.setRowCount(0)
        self.kanban_table.verticalHeader().setVisible(False)
        self.kanban_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.add_task("Сделать UI", "To Do")
        self.add_task("Проверить код", "In Progress")

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_input, alignment=Qt.AlignRight)
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

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)


        # Боковое меню
        self.menu = QListWidget()
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setFixedWidth(43)
        self.menu.setIconSize(QSize(24, 24))
        self.menu.setSpacing(7)
        self.avatar_frame = QFrame()
        self.avatar_frame.setFixedSize(80, 80)
        self.avatar_frame.setStyleSheet("border-image: url(logo-alfabank.svg);")

        # Добавляем пункты меню
        icon_path_alfa = os.path.join(os.path.dirname(__file__), "resource", "logo-alfabank.svg")
        icon_path_menu = os.path.join(os.path.dirname(__file__), "resource", "menu_icon.svg")
        icon_path_file = os.path.join(os.path.dirname(__file__), "resource", "file_icon.svg")
        icon_path_gear = os.path.join(os.path.dirname(__file__), "resource", "gear_icon.svg")
        alfa_item = QListWidgetItem(QIcon(icon_path_alfa), "")
        alfa_item.setData(Qt.UserRole, "noHover")
        alfa_item.setFlags(Qt.NoItemFlags)
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
        # self.menu.addItem(QListWidgetItem(QIcon(icon_path_menu), ""))
        # self.menu.addItem(QListWidgetItem(QIcon(icon_path_file), ""))
        # self.menu.addItem(QListWidgetItem(QIcon(icon_path_gear), ""))


        # Контентная область
        self.stack = QStackedWidget()
        self.home = HomeInterface()
        self.folder = PlaceholderInterface("Folder")
        self.settings = PlaceholderInterface("Settings")

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.folder)
        self.stack.addWidget(self.settings)
        def handle_list_change(index):
            if index > 0:
                self.stack.setCurrentIndex(index - 1)
        # Сигнал выбора
        self.menu.currentRowChanged.connect(handle_list_change)
        self.menu.setCurrentRow(1)  # по умолчанию Home

        layout.addWidget(self.menu)
        layout.addWidget(self.stack)

        self.set_icon()

    def set_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "resource", "logo-alfabank.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon not found at {icon_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Подключаем QSS (если нужно)
    qss_path = "style.qss"
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = Window()
    window.show()
    sys.exit(app.exec())