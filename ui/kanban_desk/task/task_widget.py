from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ui.utils import get_resource_path


class TaskWidget(QWidget):
    def __init__(self, task_name, number, avatar_path, tags=None):
        super().__init__()
        self.setObjectName("kanbanTaskWrapper")

        # Обёртка для применения hover
        wrapper = QFrame()
        wrapper.setObjectName("kanbanTask")
        wrapper.setAttribute(Qt.WA_Hover, True)
        wrapper.setMouseTracking(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(wrapper)

        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(10, 10, 10, 10)
        wrapper_layout.setSpacing(5)

        # Верхняя строка: аватар и текст
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Аватар
        avatar_label = QLabel()
        icon = QIcon(get_resource_path("logo-alfabank.svg"))
        pixmap = icon.pixmap(24, 24)
        avatar_label.setPixmap(pixmap)
        avatar_label.setFixedSize(24, 24)

        # Текст задачи
        text_label = QLabel(f"{task_name}.{number}")
        text_label.setObjectName("TaskText")

        top_layout.addWidget(avatar_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(text_label)

        wrapper_layout.addLayout(top_layout)

        # Нижняя строка: теги
        if tags:
            tag_layout = QHBoxLayout()
            tag_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            for tag in tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setObjectName("TaskTag")
                tag_layout.addWidget(tag_label)
            wrapper_layout.addLayout(tag_layout)