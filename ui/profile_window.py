from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLineEdit
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from PySide6.QtCore import Qt
from ui.utils import get_rounded_avatar

class ProfileWindow(QWidget):
    def __init__(self, profile_button):
        super().__init__()
        self.profile_button = profile_button
        self.setWindowTitle("Профиль пользователя")
        self.resize(400, 300)
        main_layout = QHBoxLayout(self)  # общий layout

        # ==== Левая часть (информация) ====
        info_layout = QVBoxLayout()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.email = QLineEdit()

        for field, placeholder in zip(
                [self.last_name, self.first_name, self.middle_name, self.email],
                ["Фамилия", "Имя", "Отчество", "Почта"]
        ):
            field.setPlaceholderText(placeholder)
            field.setFixedHeight(30)
            info_layout.addWidget(field)

        main_layout.addLayout(info_layout, stretch=1)

        # ==== Правая часть (аватарка) ====
        right_layout = QVBoxLayout()

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("border-radius: 50px; border: 1px solid gray;")
        self.avatar_label.setAlignment(Qt.AlignCenter)

        # начальное пустое фото
        self.avatar_label.setPixmap(QPixmap().scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.upload_button = QPushButton("Загрузить аватар")
        self.upload_button.clicked.connect(self.load_avatar)

        right_layout.addWidget(self.avatar_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        right_layout.addWidget(self.upload_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

        main_layout.addLayout(right_layout)

    def load_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
           avatar = get_rounded_avatar(file_path)
           self.avatar_label.setPixmap(avatar)
           self.profile_button.setIcon(QIcon(avatar))