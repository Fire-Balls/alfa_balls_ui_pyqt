from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from PySide6.QtCore import Qt
import os
from ui.utils import get_rounded_avatar

class ProfileWindow(QWidget):
    def __init__(self, profile_button):
        super().__init__()
        self.profile_button = profile_button
        self.setWindowTitle("Профиль пользователя")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        # Аватарка
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("border-radius: 50px; border: 1px solid gray;")
        self.avatar_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.avatar_label.setPixmap(QPixmap().scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Кнопка загрузки
        self.upload_button = QPushButton("Загрузить аватар")
        self.upload_button.clicked.connect(self.load_avatar)

        # Добавляем виджеты
        self.layout.addWidget(self.avatar_label, alignment=Qt.AlignRight | Qt.AlignTop)
        self.layout.addWidget(self.upload_button, alignment=Qt.AlignRight)

    def load_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
           avatar = get_rounded_avatar(file_path)
           self.avatar_label.setPixmap(avatar)
           self.profile_button.setIcon(QIcon(avatar))