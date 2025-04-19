import os

from PySide6.QtGui import QIcon, Qt, QAction
from PySide6.QtWidgets import \
    (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
import sys
# from ui.kanban_desk.kanban_desk import KanbanBoard
from ui.main_window import Window
# from examples.fluent_window import Window

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


        self.username_label = QLabel("LOGIN:")
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setObjectName("auth_text")

        self.username_input = create_input_with_icon("resource/user_icon.svg")
        self.username_input.setFixedWidth(250)
        self.username_input.setObjectName("auth_input")


        self.password_label = QLabel("PASSWORD:")
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setObjectName("auth_text")

        self.password_input = create_input_with_icon("resource/eye_icon.svg")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(250)
        self.password_input.setObjectName("auth_input")

        self.login_button = QPushButton("ВОЙТИ")
        self.login_button.clicked.connect(self.login) # вызываем метод
        self.login_button.setFixedWidth(250)
        self.login_button.setObjectName("enter")

        layout = QVBoxLayout()
        layout.setContentsMargins(30,0,0,15)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            # вызываем auth_service
            if username=='anton' and password=='anton':
                print('ee')
                self.kanban_board = Window() # Create a KanbanBoard instance
                print('e')
                self.kanban_board.show()  # Show the KanbanBoard
                print('22')
                self.close()  # Закрываем окно авторизации
                print('close')
                # Успешная авторизация
                # self.main_window = MainWindow(self.auth_service) # Передаем auth_service
                # self.main_window.show()
                # self.close() # Закрываем окно авторизации
                #self.close()
            else:
                QMessageBox.critical(self, "Ошибка авторизации", "Неверные имя пользователя или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

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
