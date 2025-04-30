from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtCore import Qt

from ui.utils import get_resource_path
from ui.kanban_desk.task.task_card_all_data import TaskDetailsWindow

class TaskWidget(QWidget):
    def __init__(self, task_name, number, avatar_path, title: str, tags: list[str] = None, board_prefix=""):
        super().__init__()
        self.setObjectName("kanbanTaskWrapper")
        self.task_title = title
        self.tags = tags if tags is not None else []
        task_id = f"{board_prefix}-{number}"
        self.task_name = task_name
        self.number = number
        self.avatar_path = avatar_path

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
        icon = QIcon(get_resource_path("user_icon.svg"))
        pixmap = icon.pixmap(24, 24)
        avatar_label.setPixmap(pixmap)
        avatar_label.setFixedSize(24, 24)

        # Текст задачи
        text_label = QLabel(task_name)
        text_label.setObjectName("TaskText")

        top_layout.addWidget(avatar_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(text_label)

        wrapper_layout.addLayout(top_layout)

        # Нижняя строка: префикс слева, теги справа
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Префикс задачи (например TES-3)
        prefix_label = QLabel(f"TES-{number}")
        prefix_label.setObjectName("TaskPrefix")
        bottom_layout.addWidget(prefix_label, alignment=Qt.AlignLeft)

        # Spacer между префиксом и тегами
        bottom_layout.addStretch()

        # Теги задачи (если есть)
        if self.tags:
            for tag in self.tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setObjectName("TaskTag")
                bottom_layout.addWidget(tag_label, alignment=Qt.AlignRight)

        wrapper_layout.addLayout(bottom_layout)

    def mouseDoubleClickEvent(self, event):
        # Открываем новое окно с информацией о задаче
        self.open_task_details()

    def open_task_details(self):
        """Открытие окна с деталями задачи."""
        details_window = TaskDetailsWindow(self.task_name, self.number, self.avatar_path, self.tags, parent=self)
        details_window.show()

