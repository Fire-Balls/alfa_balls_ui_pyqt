import base64
import sys
from functools import partial

from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QIcon, QImage, QAction, QPainterPath, QRegion, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QListWidget, QListWidgetItem,
    QStackedWidget, QHBoxLayout, QWidget, QVBoxLayout, QPushButton,
    QFrame, QComboBox, QToolButton, QMenu, QDialog, QLabel, QLineEdit, QDialogButtonBox
)
from PySide6.QtWidgets import QWidgetAction

from network.new.models import Board
from network.new.operations import ServiceOperations
from ui.analytics.analytic_window import AnalyticWindow
from ui.folder.folder_window import FolderWindow
from ui.kanban_desk.kanban_board import KanbanBoard
from ui.kanban_desk.task.add_task_dialog import AddTaskDialog
from ui.profile_window import ProfileWindow
from ui.setting_window.settings import PlaceholderInterface
from ui.utils import get_resource_path, get_rounded_avatar_icon_from_image


class Window(QMainWindow):
    def __init__(self, user_id, project_id, board_id, selected_project=None):
        super().__init__()


        self.user_id: int = user_id
        self.selected_project = selected_project
        self.current_project_name = ServiceOperations.get_project(project_id).name
        self.project_id = project_id
        self.user_role = None
        for user in ServiceOperations.get_project(self.project_id).users:
            if user.id == self.user_id:
                self.user_role = user.role  # Роль на проекте

        self.board = KanbanBoard(
            user_id=self.user_id,
            board_id=board_id,
            parent=self
        )

        self.setWindowTitle("Kanban Project")
        self.resize(825, 700)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(825, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet("background-color: #e0e0e0;")

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)

        self.dropdown = QComboBox()
        self.dropdown.setFixedSize(200, 40)
        self.dropdown.setObjectName("QComboTopBar")
        self.populate_projects()

        self.board_combo = QComboBox()
        self.board_combo.setFixedSize(150, 40)
        self.board_combo.setObjectName("QComboTopBar")
        self.board_combo.setEditable(False)
        self.board_combo.currentIndexChanged.connect(self.on_board_changed)
        self.board_combo.activated.connect(self.on_board_selected)

        self.update_board_combo()  # из-за этой темы не отображались столбцы с бека

        self.dropdown.activated.connect(self.on_project_selected)
        self.dropdown.currentIndexChanged.connect(self.on_project_changed)

        self.profile_button = QToolButton()
        user = ServiceOperations.get_user(user_id=self.user_id)
        image_data = None
        if user.avatar is None:
            self.profile_button.setIcon(QIcon(get_resource_path("profile_icon.svg")))
        else:
            # Строка с изображением в формате Base64
            base64_image = user.avatar
            # Декодируем строку base64 в байты
            image_data = base64.b64decode(base64_image)
            # Создаем QImage из байтов
            image = QImage()
            image.loadFromData(image_data)
            # Устанавливаем иконку из QImage
            pixmap = QPixmap.fromImage(image)
            avatar = get_rounded_avatar_icon_from_image(pixmap)
            self.profile_button.setIcon(avatar.pixmap(150, 150))

        self.profile_button.setIconSize(QSize(36, 36))
        self.profile_button.setObjectName("profile_button")
        self.profile_button.setFocusPolicy(Qt.NoFocus)
        self.profile_button.setPopupMode(QToolButton.InstantPopup)

        # Отображение роли под аватаркой пользователя
        self.role_label = QLabel(self.user_role)

        # Кнопка список пользователей на проекте
        self.user_list_button = QToolButton(self)
        self.user_list_button.setIcon(QIcon(get_resource_path("user_list_icon.png")))
        self.user_list_button.setIconSize(QSize(36, 36))
        self.user_list_button.setObjectName("user_list_button")
        self.user_list_button.setFocusPolicy(Qt.NoFocus)
        self.user_list_button.setPopupMode(QToolButton.InstantPopup)
        # Сам список пользователей
        self.users_list = QListWidget()
        self.users_list.setObjectName("users_list_widget")
        self.users_list.setFixedSize(QSize(200, 150))

        self.all_users = ServiceOperations.get_project(self.project_id).users
        for user in self.all_users:
            QListWidgetItem(f"{user.full_name}, Роль: {user.role}", self.users_list)

        self.add_task_dialog = AddTaskDialog(self.users_list)

        buttons_layout = QHBoxLayout()
        # Само меню, округлое QMenu чекните RoundedMenu если интересно
        self.menu = RoundedMenu(self)

        menu_layout = QVBoxLayout(self.menu)
        menu_layout.setContentsMargins(4, 4, 4, 8)
        if self.user_role == "OWNER":
            buttons_layout.addStretch()
            self.menu.setFixedSize(215, 190)
            # Кнопки добавления и удаления пользователя
            self.delete_user_button = QPushButton("Удалить")
            self.delete_user_button.setObjectName("user_list_buttons")
            self.delete_user_button.setFixedSize(90, 20)
            # к кнопке при нажатии подключается функция.
            self.delete_user_button.clicked.connect(lambda: self.delete_user())

            # Кнопка Добавить пользователя на проект
            self.add_user_button = QPushButton("Добавить")
            self.add_user_button.setObjectName("user_list_buttons")
            self.add_user_button.setFixedSize(90, 20)
            self.add_user_button.clicked.connect(lambda: self.add_user())

            buttons_layout.addWidget(self.delete_user_button)
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.add_user_button)
        else:
            self.menu.setFixedSize(215, 170)

        menu_layout.addWidget(self.users_list)
        menu_layout.addStretch()
        menu_layout.addLayout(buttons_layout)
        # Список людей на проекте чисто визуал
        self.list_action = QWidgetAction(self.menu)
        self.list_action.setDefaultWidget(self.users_list)

        # Добавляем список людей в менюшку
        self.menu.addAction(self.list_action)
        # добавляем при нажатии кнопки открытие меню
        self.user_list_button.setMenu(self.menu)
        # Layout для нормального расположения
        avatar_layout = QVBoxLayout()
        avatar_layout.addWidget(self.profile_button)
        avatar_layout.addWidget(self.role_label)

        # Профиль
        self.profile_window = None
        profile_menu = RoundedMenu(self, radius=16)
        profile_action = QAction("Профиль", self)
        profile_action.triggered.connect(partial(self.open_profile_window, image_data, user_id))
        profile_menu.addAction(profile_action)
        profile_menu.addAction(QAction("Настройки", self))
        profile_menu.addSeparator()
        profile_exit = QAction("Выход", self)
        profile_exit.triggered.connect(self.logout)
        profile_menu.addAction(profile_exit)
        profile_menu.aboutToShow.connect(self.show_profile_border)
        profile_menu.aboutToHide.connect(self.hide_profile_border)
        self.profile_button.setMenu(profile_menu)

        top_layout.addWidget(QLabel("Проект"))
        top_layout.addWidget(self.dropdown)
        top_layout.addWidget(QLabel("Доска"))
        top_layout.addWidget(self.board_combo)
        top_layout.addStretch()
        top_layout.addWidget(self.user_list_button)
        top_layout.addLayout(avatar_layout)
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
        self.stack.addWidget(self.board)
        self.folder_window = FolderWindow()
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

        # if self.selected_project:
        #     self.load_project(self.selected_project)

        # self.dropdown.currentTextChanged.connect(self.update_folder_window)

    def on_menu_changed(self, index):
        if index > 0:
            self.stack.setCurrentIndex(index - 1)

    def show_profile_border(self):
        self.profile_button.setStyleSheet("""
            QToolButton#profile_button {
                border: 2px solid #ee3424;
                border-radius: 16px;
                padding: 2px;
            }
        """)

    def hide_profile_border(self):
        self.profile_button.setStyleSheet("""
            QToolButton#profile_button {
                border: 2px solid transparent;
                border-radius: 16px;
                padding: 2px;
            }
        """)

    def open_profile_window(self, img, user_id):
        if self.profile_window is None:
            self.profile_window = ProfileWindow(self.profile_button, img, user_id)
        self.profile_window.show()
        self.profile_window.raise_()
        self.profile_window.activateWindow()

    def populate_projects(self):
        self.dropdown.clear()

        projects = ServiceOperations.get_all_projects_by_user(self.user_id)
        self.dropdown.addItems([project.name for project in projects])
        self.dropdown.addItem("➕ Добавить проект")

        if self.selected_project:
            index = self.dropdown.findText(self.selected_project)
            if index != -1:
                self.dropdown.setCurrentIndex(index)

    def on_project_selected(self, index):
        selected_text = self.dropdown.itemText(index)
        if selected_text == "➕ Добавить проект":
            previous_project = self.current_project_name

            dialog = AddProjectDialog(self)
            if dialog.exec():
                project_name = dialog.get_project_name()
                board_name = dialog.get_board_name()
                if project_name:
                    ServiceOperations.create_new_project_with_board(project_name, board_name, "OWNER", self.user_id)
                    self.populate_projects()
                    project_index = self.dropdown.findText(project_name)
                    if project_index != -1:
                        self.dropdown.setCurrentIndex(project_index)
                        self.current_project_name = project_name
                        self.load_project(project_name)

                else:
                    self.populate_projects()
                    project_index = self.dropdown.findText(previous_project)
                    if project_index != -1:
                        self.dropdown.setCurrentIndex(project_index)
            else:
                self.populate_projects()
                project_index = self.dropdown.findText(previous_project)
                if project_index != -1:
                    self.dropdown.setCurrentIndex(project_index)
        else:
            selected_project = selected_text
            self.current_project_name = selected_project
            print(f"Открываем проект: {selected_project}")

    def on_project_changed(self, index):
        selected_text = self.dropdown.itemText(index)
        if selected_text == "➕ Добавить проект" or index == -1:
            return

        self.current_project_name = selected_text
        self.load_project(selected_text)

        retrieved_project = ServiceOperations.get_project(self.project_id)
        boards = retrieved_project.boards
        boards_names = [board.name for board in boards]

        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        self.board_combo.addItems(boards_names)
        if self.user_role == "OWNER":
            self.board_combo.addItem("➕ Добавить доску")
        self.board_combo.blockSignals(False)

        if not boards:
            return

        current_board = boards[0]
        if current_board and current_board in boards:
            index = self.board_combo.findText(current_board.name)
            self.board_combo.setCurrentIndex(index)
        else:
            self.board_combo.setCurrentIndex(0)

    def load_project(self, project_name):
        loaded_project = ServiceOperations.get_project_by_name(project_name, self.user_id)
        full_loaded_project = ServiceOperations.get_project(loaded_project.id)
        self.current_project_name = full_loaded_project.name
        self.project_id = full_loaded_project.id

        # self.update_board_combo() #todo

        boards = full_loaded_project.boards
        if boards:
            full_first_board = ServiceOperations.get_board(self.project_id, boards[0].id)
            self.set_current_board(full_first_board)

    # def update_folder_window(self, project_name):
    #     if project_name and project_name != "➕ Добавить проект":
    #         self.folder_window.set_project(project_name)

    # При смене доски не появляются задачи из JSOn, при повторной смене на прошлую доску, удаляется из JSON все задачи, т.к. в UI пустые колонки
    # Также пофиксить хуйню с трёмя открывающимися окнами при создании доски
    def on_board_changed(self, index):
        selected_board = self.board_combo.itemText(index)
        if selected_board == "➕ Добавить доску":
            return

        self.board.board_name = selected_board
        self.load_board(selected_board)

    def update_board_combo(self):
        self.board_combo.blockSignals(True)
        self.board_combo.clear()

        boards = ServiceOperations.get_project(self.project_id).boards
        print('update_board_combo', boards)
        boards_names = [board.name for board in boards]

        self.board_combo.addItems(boards_names)
        if self.user_role == "OWNER":
            self.board_combo.addItem("➕ Добавить доску")

        current_board = ServiceOperations.get_board(self.project_id, self.board.board_id)

        if current_board:
            index = self.board_combo.findText(current_board.name)
            self.board_combo.setCurrentIndex(index)
            self.load_board(current_board.name)
        elif boards:
            self.board_combo.setCurrentIndex(0)
            self.load_board(boards[0].name)

        self.board_combo.blockSignals(False)

    def set_current_board(self, board: Board):
        self.board.board_name = board.name
        self.board.set_project_and_board(ServiceOperations.get_project(self.project_id), board)
        print(board.id)
        # self.folder_window.set_project(self.current_project_name)

    def load_board(self, board_name: str):
        print(f"[LOAD BOARD] Загружаем доску: {board_name}")

        # for i in reversed(range(self.board.board_layout.count())):
        #     widget_item = self.board.board_layout.itemAt(i)
        #     widget = widget_item.widget()
        #     if widget:
        #         widget.setParent(None)

        current_project = ServiceOperations.get_project(self.project_id)
        board_data = None
        for board in current_project.boards:
            if board.name == board_name:
                board_data = ServiceOperations.get_board(current_project.id, board.id)

        print('board from backend', board_data)
        self.board.board_name = board_data.name
        self.board.board_id = board_data.id
        self.board.project_name = self.current_project_name

        self.board.clear_board()
        for status in board_data.statuses:
            self.board.add_column(status.name, status.id)
        print('UI BOARD status', self.board.columns, self.board.board_id, self.board.board_name)
        print()
        for issue in board_data.issues:
            self.board.add_task(issue)

    def on_board_selected(self, index):
        selected_text = self.board_combo.itemText(index)
        if selected_text == "➕ Добавить доску":
            dialog = AddBoardDialog(self)
            if dialog.exec():
                board_name = dialog.get_board_name()
                if board_name:
                    created_board = ServiceOperations.create_new_board(self.project_id, board_name)
                    self.update_board_combo()
                    board_index = self.board_combo.findText(board_name)
                    if board_index != -1:
                        self.board_combo.setCurrentIndex(board_index)
                        self.load_board(board_name)
        else:
            self.load_board(selected_text)

    # Тестовый метод для удаление пользователя. Заглушка, делайте что хотите
    def delete_user(self):
        select_item = self.users_list.selectedItems()
        user_to_delete = select_item[0].text().split(", Роль:")[0]
        for user in ServiceOperations.get_project(self.project_id).users:
            if user.full_name == user_to_delete:
                ServiceOperations.delete_user_from_project(self.project_id, user.id)
                if self.user_id == user.id:
                    sys.exit()

        for item in select_item:
            self.users_list.takeItem(self.users_list.row(item))

    # Метод для добавления пользователя на проект. Нужно сделать на беке сравнение почты и находить юзера. Иначе вернуть ошибку
    def add_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Пригласить Пользователя")
        dialog.setFixedSize(300, 160)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        label = QLabel("Введите почту пользователя")
        # Поле ввода
        email_input = QLineEdit()
        email_input.setPlaceholderText("example@mail.ru")

        role_label = QLabel("Выберите роль пользователя")
        role_input = QComboBox()
        role_input.setObjectName("QComboTopBar")
        role_input.addItem("OWNER")
        role_input.addItem("PARTICIPANT")


        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        # Кнопки отмена и Пригласить
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        invite_button = QPushButton("Пригласить")
        invite_button.clicked.connect(lambda: self.add_user_by_email(email_input.text(), role_input.currentText(), dialog))

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(invite_button)

        layout.addWidget(label)
        layout.addWidget(email_input)
        layout.addWidget(role_label)
        layout.addWidget(role_input)
        layout.addStretch()
        layout.addLayout(buttons_layout)

        dialog.exec()

    def add_user_by_email(self, email: str, selected_role: str, dialog: QDialog):
        user_to_add = ServiceOperations.get_user_by_email(email)
        user_role = selected_role
        ServiceOperations.put_user_in_project(self.project_id, user_to_add.id, user_role)

        role = "OWNER" if user_role == "OWNER" else "PARTICIPANT"  # todo пока так коряво, потом поправлю
        QListWidgetItem(f"{user_to_add.full_name}, Роль: {role}", self.users_list)

        dialog.close()

    def get_user_names(self) -> list[str]:
        names = []
        for i in range(self.users_list.count()):
            item_text = self.users_list.item(i).text()
            name = item_text.split(",")[0].strip()
            names.append(name)
        return names

    def logout(self):
        from ui.auth_window.auth_win import AuthWindow
        self.close()
        self.auth_win = AuthWindow()
        self.auth_win.show()


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
