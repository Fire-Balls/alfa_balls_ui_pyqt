import os


from PySide6.QtWidgets import QToolButton
from PySide6.QtGui import Qt, QAction, QIcon
from PySide6.QtWidgets import \
    (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
import sys

from ui.utils import get_resource_path, ProjectManager
from ui.project_making_window.project_selection_window import ProjectSelectionWindow
# from network.new.client_manage import get_client
from network.new.client_manage import ClientManager

def create_input_with_icon(icon_path):
    line_edit = QLineEdit()
    action = QAction(QIcon(icon_path), "", line_edit)
    line_edit.addAction(action, QLineEdit.TrailingPosition)
    return line_edit


class AuthWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 350)
        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))

        self.username_label = QLabel("LOGIN")
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setObjectName("auth_text")

        self.username_input = create_input_with_icon(get_resource_path("user_icon.svg"))
        self.username_input.setFixedWidth(250)
        self.username_input.setObjectName("auth_input")

        self.host_label = QLabel("HOST")
        self.host_label.setAlignment(Qt.AlignCenter)
        self.host_label.setObjectName("auth_text")

        self.host_input = create_input_with_icon(get_resource_path("host_icon.svg"))
        self.host_input.setFixedWidth(250)
        self.host_input.setObjectName("auth_input")

        # Загружаем хост из файла и устанавливаем в поле, если есть
        saved_host = ClientManager.load_host_from_file()
        if saved_host:
            self.host_input.setText(saved_host)

        self.password_label = QLabel("PASSWORD")
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setObjectName("auth_text")
        self.password_input = PasswordLineEdit(self)

        self.login_button = QPushButton("ВОЙТИ")
        self.login_button.clicked.connect(self.login) # вызываем метод
        self.login_button.setFixedWidth(250)
        self.login_button.setObjectName("enter")

        layout = QVBoxLayout()
        layout.setContentsMargins(30,0,0,75)

        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        current_host = self.host_input.text()
        saved_host = ClientManager.load_host_from_file()
        # Если хост изменился или пустой, сохраняем новый
        if current_host and current_host != saved_host:
            ClientManager.save_host_to_file(current_host)
        ClientManager(current_host)
        try:
            # вызываем auth_service
            # if username=='super@urfu.ru' and password=='super
            if username=='1' and password=='1' or ClientManager().client.login(username, password):
                # client_manager.client.login("super123@urfu.ru", "super")
            # if username=='1' and password=='1':
                print('ee')
                self.project_manager = ProjectManager()
                self.project_selection_window = ProjectSelectionWindow(self.project_manager)
                self.project_selection_window.show()
                self.close()
                print('close')
            # else:
            #     QMessageBox.critical(self, "Ошибка авторизации", "Неверные имя пользователя или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

    def keyPressEvent(self, event):
        # если нажата клавиша Enter (Qt.Key_Return или Qt.Key_Enter)
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.login() # Вызываем метод входа
            event.accept()

def run():
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к папке 'ui'
    ui_dir = os.path.dirname(current_dir)

    # Путь к .qss файлу
    style_path = os.path.join(ui_dir, 'style', 'style.qss')

    # Загружаем qss
    with open(style_path, 'r', encoding='utf-8') as f:
        QApplication.instance().setStyleSheet(f.read())
    auth_win = AuthWindow()
    auth_win.show()
    sys.exit(app.exec())

class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.setObjectName("auth_input")
        self.setFixedWidth(250)

        # Кнопка-глаз
        self.toggle_button = QToolButton(self)
        self.toggle_button.setIcon(QIcon(get_resource_path("eye_hidden_icon.svg")))
        # print(get_resource_path("eye_hidden_icon.svg"))
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet("border: none;")
        self.toggle_button.setFixedSize(24, 24)

        # Позиция справа

        self.setTextMargins(0, 0, self.toggle_button.width() +5, 0)

        self.toggle_button.move(self.rect().right() - self.toggle_button.width() -  5,
                                (self.rect().height() - self.toggle_button.height()) // 2)

        self.toggle_button.clicked.connect(self.toggle_password_visibility)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toggle_button.move(self.rect().right() - self.toggle_button.width() - 5,
                                (self.rect().height() - self.toggle_button.height()) // 2)

    def toggle_password_visibility(self):
        if self.echoMode() == QLineEdit.Password:
            self.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setIcon(QIcon(get_resource_path("eye_visible_icon.svg")))
        else:
            self.setEchoMode(QLineEdit.Password)
            self.toggle_button.setIcon(QIcon(get_resource_path("eye_hidden_icon.svg")))
