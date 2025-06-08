from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon, QPixmap

from ui.kanban_desk.task.task_card_all_data import TaskDetailsWindow
from ui.utils import get_resource_path


class TaskWidget(QWidget):
    def __init__(self, id , number, title: str, tags: list[str] = None, is_important=False,
                 #avatar_path, board_prefix="",description, start_datetime=None, end_datetime=None,
                 assignee=""):
        super().__init__()
        self.setObjectName("kanbanTaskWrapper")
        self.id = id
        # self.type = type
        self.setFixedWidth(215)
        self.tags = tags if tags is not None else []
        self.title = title
        # self.description = description
        self.code = number
        self.assignee = assignee
        # self.avatar_path = avatar_path
        self.is_important = is_important
        # self.start_datetime = start_datetime or QDateTime.currentDateTime()
        # self.end_datetime = end_datetime or QDateTime.currentDateTime().addDays(3)

        # Обёртка для применения hover
        wrapper = QFrame()
        wrapper.setObjectName("kanbanTask")
        if self.is_important:
            wrapper.setStyleSheet("""
                #kanbanTask {
                    border: 2px solid red;
                    border-radius: 8px;
                    padding: 6px;
                }
            """)
        else:
            wrapper.setStyleSheet("""
                #kanbanTask {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 6px;
                }
            """)
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
        text_label = QLabel(title)
        text_label.setObjectName("TaskText")

        top_layout.addWidget(avatar_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(text_label)

        wrapper_layout.addLayout(top_layout)

        executor_layout = QHBoxLayout()
        self.executor_label = QLabel(assignee if assignee else "Не назначен")
        self.executor_label.setStyleSheet("color: #555; font-size: 11px;")
        executor_layout.addWidget(self.executor_label)
        executor_layout.addStretch()

        wrapper_layout.addLayout(executor_layout)

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
        self.open_task_details()

    def open_task_details(self):
        """Открытие окна с деталями задачи."""
        details_window = TaskDetailsWindow(
            self.title,
            self.description,
            self.code,
            self.avatar_path,
            self.tags,
            self.is_important,
            self.start_datetime,
            self.end_datetime,
            executor=self.executor_label.text() if hasattr(self, 'executor_label') else "",
            files=getattr(self, 'files', []),
            parent=self
        )
        details_window.show()