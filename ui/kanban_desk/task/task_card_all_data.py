from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QDialogButtonBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from datetime import timedelta, datetime
from ui.utils import get_resource_path


class TaskDetailsWindow(QDialog):
    """Окно с детальной информацией о задаче."""

    def __init__(self, task_name, number, avatar_path=None, tags=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Детали задачи")
        self.setFixedSize(325,300)
        self.task_name = task_name
        self.number = number
        self.avatar_path = avatar_path
        self.tags = tags or []

        layout = QVBoxLayout(self)

        # Информация о задаче
        layout.addWidget(QLabel(f"<b>Задача:</b> {self.task_name}"))
        layout.setSpacing(5)
        layout.addWidget(QLabel(f"<b>Описание:</b> Сделать задачу в срок и быстро! "))
        layout.setSpacing(5)
        layout.addWidget(QLabel(f"<b>Номер:</b> {self.number}"))
        layout.addWidget(QLabel(f"<b>Дата начала:</b> {datetime.now().strftime('%Y-%m-%d    %H:00')}"))
        layout.addWidget(QLabel(f"<b>Дедлайн:</b> {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d    %H:00')}"))

        # Аватар (если есть)
        if self.avatar_path:
            pixmap = QPixmap(self.avatar_path)
            avatar_label = QLabel()
            avatar_label.setPixmap(pixmap.scaledToWidth(100))
            layout.addWidget(avatar_label)

        # Теги
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("<b>Теги:</b>"))
        for tag in self.tags:
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("background-color: lightblue; border-radius: 5px; padding: 2px;")
            tags_layout.addWidget(tag_label)

        layout.addLayout(tags_layout)

        # Кнопки "ОК" и "Отмена"
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)  # Закрытие окна при нажатии "ОК"
        layout.addWidget(button_box)