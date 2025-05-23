import os
import sys

from PySide6.QtCore import Qt, QSize, QRectF, QDateTime
from PySide6.QtGui import QIcon, QAction, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
    QFrame, QComboBox, QToolButton, QMenu, QDialog, QLabel, QLineEdit, QDialogButtonBox
)

from ui.analytics.analytic_window import AnalyticWindow
from ui.folder.folder_window import FolderWindow
from ui.kanban_desk.kanban_board import KanbanBoard
from ui.profile_window import ProfileWindow
from ui.utils import get_resource_path, ProjectManager


class PlaceholderInterface(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QPushButton(f"{title} content"))


class Window(QMainWindow):
    def __init__(self, selected_project=None):
        super().__init__()
        self.selected_project = selected_project
        self.current_project_name = ""
        self.projects_manager = ProjectManager()

        self.current_project_name = None
        self.selected_board = None
        self.kanban_board = KanbanBoard(
            project_manager=self.projects_manager,
            board_name=self.selected_board,
            project_name=self.selected_project
        )
        self.setWindowTitle("Kanban Project")
        self.resize(825, 700)
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
        self.dropdown.setObjectName("QComboTopBar")
        self.populate_projects()

        self.board_combo = QComboBox()
        self.board_combo.setObjectName("QComboTopBar")
        self.board_combo.setEditable(False)
        self.board_combo.currentIndexChanged.connect(self.on_board_changed)
        self.board_combo.activated.connect(self.on_board_selected)

        self.update_board_combo()

        self.dropdown.activated.connect(self.on_project_selected)
        self.dropdown.currentIndexChanged.connect(self.on_project_changed)

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

        top_layout.addWidget(QLabel("Проект"))
        top_layout.addWidget(self.dropdown)
        top_layout.addWidget(QLabel("Доска"))
        top_layout.addWidget(self.board_combo)
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

        analytic_item = QListWidgetItem(QIcon(get_resource_path("analytic_icon.svg")), "")
        file_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(analytic_item)

        gear_item = QListWidgetItem(QIcon(get_resource_path("gear_icon.svg")), "")
        gear_item.setSizeHint(QSize(30, 30))
        self.menu.addItem(gear_item)

        self.stack = QStackedWidget()
        self.board = KanbanBoard(self.projects_manager, self.selected_board, self.selected_project, parent=None)
        self.stack.addWidget(self.board)
        os.path.dirname(self.projects_manager.file_path)
        self.folder_window = FolderWindow(self.projects_manager)
        self.analytic = AnalyticWindow()
        self.settings = PlaceholderInterface("Settings")

        self.stack.addWidget(self.folder_window)
        self.stack.addWidget(self.analytic)
        self.stack.addWidget(self.settings)

        self.menu.currentRowChanged.connect(self.on_menu_changed)
        self.menu.setCurrentRow(1)

        content_layout.addWidget(self.menu)
        content_layout.addWidget(self.stack)

        main_layout.addLayout(content_layout)

        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))

        if self.selected_project:
            self.load_project(self.selected_project)

        self.dropdown.currentTextChanged.connect(self.update_folder_window)

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
        self.dropdown.addItems(self.projects_manager.get_projects())
        self.dropdown.addItem("➕ Добавить проект")

        if self.selected_project:
            index = self.dropdown.findText(self.selected_project)
            if index != -1:
                self.dropdown.setCurrentIndex(index)

    def on_project_selected(self, index):
        selected_text = self.dropdown.itemText(index)
        if selected_text == "➕ Добавить проект":
            # Запоминаем ТЕКУЩИЙ выбранный проект в переменную
            previous_project = self.current_project_name

            # Открываем диалог добавления проекта
            dialog = AddProjectDialog(self)
            if dialog.exec():
                project_name = dialog.get_project_name()
                board_name = dialog.get_board_name()
                if project_name:
                    self.projects_manager.add_project(project_name, board_name)
                    self.populate_projects()
                    project_index = self.dropdown.findText(project_name)
                    if project_index != -1:
                        self.dropdown.setCurrentIndex(project_index)
                        self.current_project_name = project_name  # Обновляем текущий проект
                else:
                    # Название пустое — вернуть предыдущий проект
                    self.populate_projects()
                    project_index = self.dropdown.findText(previous_project)
                    if project_index != -1:
                        self.dropdown.setCurrentIndex(project_index)
            else:
                # Диалог закрыли — вернуть предыдущий проект
                self.populate_projects()
                project_index = self.dropdown.findText(previous_project)
                if project_index != -1:
                    self.dropdown.setCurrentIndex(project_index)
        else:
            selected_project = selected_text
            self.current_project_name = selected_project  # Сохраняем выбранный проект
            print(f"Открываем проект: {selected_project}")

    def on_project_changed(self, index):
        selected_text = self.dropdown.itemText(index)
        if selected_text == "➕ Добавить проект":
            return

        # Сохраняем текущие данные перед сменой
        if self.current_project_name and self.board.board_name:
            project = self.projects_manager.projects.get(self.current_project_name)
            if project:
                project["boards"][self.board.board_name] = self.board.save_tasks()
                self.projects_manager.save_projects()

        # Загружаем новый проект
        self.current_project_name = selected_text
        self.load_project(selected_text)

        project_data = self.projects_manager.projects.get(self.current_project_name, {})
        boards = project_data.get("boards", {})

        self.board_combo.blockSignals(True)  # отключаем сигналы, чтобы не вызывался on_board_changed
        self.board_combo.clear()
        self.board_combo.addItems(boards.keys())
        self.board_combo.addItem("➕ Добавить доску")
        self.board_combo.blockSignals(False)

        if not boards:
            return  # Нет досок — выходим, не выбираем ничего автоматически

        # Выбираем текущую доску, если указана
        current_board = project_data.get("current_board")
        if current_board and current_board in boards:
            index = self.board_combo.findText(current_board)
            self.board_combo.setCurrentIndex(index)
        else:
            self.board_combo.setCurrentIndex(0)

    def load_project(self, project_name):
        self.current_project_name = project_name
        self.projects_manager.set_current_project(project_name)
        self.update_board_combo()

        # Загружаем первую доску проекта
        boards = self.projects_manager.get_boards(project_name)
        if boards:
            self.set_current_board(boards[0], project_name)

    def update_folder_window(self, project_name):
        if project_name and project_name != "➕ Добавить проект":
            self.folder_window.set_project(project_name)

    #При смене доски не появляются задачи из JSOn, при повторной смене на прошлую доску, удаляется из JSON все задачи, т.к. в UI пустые колонки
    # Также пофиксить хуйню с трёмя открывающимися окнами при создании доски
    def on_board_changed(self, index):
        selected_board = self.board_combo.itemText(index)
        if selected_board == "➕ Добавить доску":
            return

        # Сохраняем старую доску
        if self.current_project_name and self.board.board_name:
            project = self.projects_manager.projects.get(self.current_project_name)
            if project:
                project["boards"][self.board.board_name] = self.board.save_tasks()
                project["current_board"] = self.board.board_name
                self.projects_manager.save_projects()

        # Загружаем новую доску
        self.board.board_name = selected_board
        self.load_board(selected_board)

        # Обновляем текущую доску в проекте
        project = self.projects_manager.projects.get(self.current_project_name)
        if project:
            project["current_board"] = selected_board
            self.projects_manager.save_projects()

    def update_board_combo(self):
        self.board_combo.blockSignals(True)
        self.board_combo.clear()

        boards = self.projects_manager.get_boards(self.current_project_name)
        self.board_combo.addItems(boards)
        self.board_combo.addItem("➕ Добавить доску")

        # Установить текущую доску из JSON
        current_board = self.projects_manager.projects.get(self.current_project_name, {}).get("current_board")
        if current_board and current_board in boards:
            index = self.board_combo.findText(current_board)
            self.board_combo.setCurrentIndex(index)
            self.load_board(current_board)
        elif boards:
            self.board_combo.setCurrentIndex(0)
            self.load_board(boards[0])

        self.board_combo.blockSignals(False)

    def set_current_board(self, board_name, project_name):
        self.board.board_name = board_name
        self.projects_manager.set_current_board(project_name, board_name)
        self.board.set_project_and_board(self.current_project_name, board_name)
        self.folder_window.set_project(self.current_project_name)

    def load_board(self, board_name: str):
        print(f"[LOAD BOARD] Загружаем доску: {board_name}")

        # Очистка старых колонок
        for i in reversed(range(self.board.board_layout.count())):
            widget_item = self.board.board_layout.itemAt(i)
            widget = widget_item.widget()
            if widget:
                widget.setParent(None)
        self.board.columns.clear()

        # === Обновляем название активной доски и проекта ===
        self.board.board_name = board_name
        self.board.project_name = self.current_project_name

        # Получаем данные из JSON
        board_data = self.board.project_manager.get_tasks(self.current_project_name, board_name)

        for column_name, tasks in board_data.items():
            self.board.add_column(column_name)  # Создаём колонку через стандартный метод

            for task_data in tasks:
                task_name = task_data.get("task_name", "Без названия")
                description = task_data.get("description")
                number = task_data.get("number")
                tags = task_data.get("tags", [])
                is_important = task_data.get("is_important", False)
                start_datetime = task_data.get("start_datetime")
                end_datetime = task_data.get("end_datetime")
                executor = task_data.get("executor", "")
                files = task_data.get("files", [])

                # Добавляем задачу без дублирования
                self.board.add_task(
                    task_name=task_name,
                    description=description,
                    column_name=column_name,
                    tags=tags,
                    files=files,
                    number=number,
                    save_to_json=False,  # уже загружено из JSON
                    is_important=is_important,
                    start_datetime=QDateTime.fromString(start_datetime, Qt.ISODate) if start_datetime else None,
                    end_datetime=QDateTime.fromString(end_datetime, Qt.ISODate) if end_datetime else None,
                    executor=executor
                )

    def on_board_selected(self, index):
        selected_text = self.board_combo.itemText(index)
        if selected_text == "➕ Добавить доску":
            dialog = AddBoardDialog(self)
            if dialog.exec():
                board_name = dialog.get_board_name()
                if board_name:
                    self.projects_manager.create_board(self.current_project_name, board_name)
                    self.update_board_combo()
                    board_index = self.board_combo.findText(board_name)
                    if board_index != -1:
                        self.board_combo.setCurrentIndex(board_index)
                        self.load_board(board_name)
        else:
            self.load_board(selected_text)



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

        self.label_board_name = QLabel("Введите название доски:")
        self.layout.addWidget(self.label_board_name)
        self.board_input = QLineEdit()
        self.layout.addWidget(self.board_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.layout.addWidget(self.error_label)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.validate_and_accept)
        self.layout.addWidget(self.add_button)

    def get_project_name(self):
        return self.name_input.text().strip()

    def get_board_name(self):
        return self.board_input.text().strip()

    def validate_and_accept(self):
        name = self.get_project_name()
        if not name:
            self.error_label.setText("Название проекта не может быть пустым.")
            return
        if self.project_manager and name in self.project_manager.get_projects():
            self.error_label.setText("Проект с таким названием уже существует.")
            return
        self.accept()

class AddBoardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить доску")
        self.layout = QVBoxLayout(self)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Введите название доски")
        self.layout.addWidget(self.name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_board_name(self):
        return self.name_input.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
