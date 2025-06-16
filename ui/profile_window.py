import base64
from tkinter.font import names

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLineEdit
from PySide6.QtGui import QPixmap, QIcon, QImage
from PySide6.QtCore import Qt

from network.new.operations import ServiceOperations
from ui.utils import get_rounded_avatar_icon, get_rounded_avatar_icon_from_image


class ProfileWindow(QWidget):
    def __init__(self, profile_button, avatar, user_id, user):
        super().__init__()
        self.profile_button = profile_button
        self.setWindowTitle("Профиль пользователя")
        self.resize(350, 150)
        self.user_id = user_id
        self.avatar_base64 = avatar
        main_layout = QHBoxLayout(self)  # общий layout

        # ==== Левая часть (информация) ====
        info_layout = QVBoxLayout()
        self.name_label = QLabel("<b>ФИО</b>")
        self.name = QLineEdit(user.full_name) # ФИО пользователя
        self.email_label = QLabel("<b>Почта</b>")
        self.email = QLineEdit(user.email) # Почта пользователя
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.name)
        info_layout.addWidget(self.email_label)
        info_layout.addWidget(self.email)

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

        self.save_button = QPushButton("Сохранить")
        self.save_button.setFixedSize(128, 25)
        self.save_button.clicked.connect(self.save_changes)

        right_layout.addWidget(self.avatar_label, alignment=Qt.AlignTop | Qt.AlignHCenter)
        right_layout.addWidget(self.upload_button, alignment=Qt.AlignTop | Qt.AlignHCenter)
        right_layout.addWidget(self.save_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

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

    def save_changes(self):
         #todo сделать сохранение изменений при вводе новых данных, ФИО и почты



        self.close() # Оставить в конце, чтобы закрыть окно профиля