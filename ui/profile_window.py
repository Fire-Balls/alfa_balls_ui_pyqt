import base64

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLineEdit
from PySide6.QtGui import QPixmap, QIcon, QImage
from PySide6.QtCore import Qt

from network.new.operations import ServiceOperations
from ui.utils import get_rounded_avatar_icon, get_rounded_avatar_icon_from_image


class ProfileWindow(QWidget):
    def __init__(self, profile_button, avatar, user_id):
        super().__init__()
        self.profile_button = profile_button
        self.setWindowTitle("Профиль пользователя")
        self.resize(400, 300)
        self.user_id = user_id
        self.avatar_base64 = avatar
        main_layout = QHBoxLayout(self)  # общий layout

        # ==== Левая часть (информация) ====
        info_layout = QVBoxLayout()
        self.first_name = QLineEdit("Иван")
        self.last_name = QLineEdit("Иванов")
        self.middle_name = QLineEdit("Иванович")
        self.email = QLineEdit("i.i.i@urfu.me")

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

        if self.avatar_base64 is not None:
            image = QImage()
            image.loadFromData(self.avatar_base64)
            pixmap = QPixmap.fromImage(image)
            avatar = get_rounded_avatar_icon_from_image(pixmap)
            self.avatar_label.setPixmap(avatar.pixmap(150, 150))
            self.profile_button.setIcon(QIcon(avatar))
        else:
            self.avatar_label.setPixmap(QPixmap().scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.upload_button = QPushButton("Загрузить аватар")
        self.upload_button.clicked.connect(self.load_avatar)

        right_layout.addWidget(self.avatar_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        right_layout.addWidget(self.upload_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

        main_layout.addLayout(right_layout)

    def load_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            avatar = get_rounded_avatar_icon(file_path)
            self.avatar_label.setPixmap(avatar.pixmap(150, 150))
            self.profile_button.setIcon(QIcon(avatar))
            res = ServiceOperations.get_user(user_id=self.user_id)
            print(res)
            ServiceOperations.update_user(res.id, res.full_name, res.email, file_path, res.role)
