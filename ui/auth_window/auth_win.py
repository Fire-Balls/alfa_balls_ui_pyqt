from PySide6.QtWidgets import \
    (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
import sys
# from ui.kanban_desk.kanban_desk import KanbanBoard
from ui.main_window import Window
# from examples.fluent_window import Window

class AuthWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login) # вызваем метод

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

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
    auth_win = AuthWindow()
    auth_win.show()
    sys.exit(app.exec())
