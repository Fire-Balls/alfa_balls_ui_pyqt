import base64

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon, QPixmap, QImage

from network.new.models import User
from ui.kanban_desk.task.task_card_all_data import TaskDetailsWindow
from ui.utils import get_resource_path, get_rounded_avatar_icon_from_image
from network.new.operations import ServiceOperations


class TaskWidget(QWidget):
    def __init__(self, issue_id: int, code: str, issue_type: str, title: str, assignee: User,
                 tags: list[str] = None, is_important=False,
                 # avatar_path, board_prefix="",description, start_datetime=None, end_datetime=None,
                 ):
        super().__init__()
        self.setObjectName("kanbanTaskWrapper")
        self.id = issue_id
        self.type_name = issue_type
        self.setFixedWidth(215)
        self.tags = tags if tags is not None else []
        self.title = title
        # self.description = description
        self.code = code
        self.assignee_name = assignee.full_name if assignee is not None else ""
        self.assignee_avatar = assignee.avatar if assignee is not None else None
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
        if self.assignee_avatar is None:
            icon = QIcon(get_resource_path("user_icon.svg"))
            pixmap = icon.pixmap(24, 24)
            avatar_label.setPixmap(pixmap)
            avatar_label.setFixedSize(24, 24)
        else:
            base64_image = self.assignee_avatar
            image_data = base64.b64decode(base64_image)
            image = QImage()
            image.loadFromData(image_data)
            pixmap = QPixmap.fromImage(image)
            avatar = get_rounded_avatar_icon_from_image(pixmap)
            pixmap = avatar.pixmap(24, 24)
            avatar_label.setPixmap(pixmap)
            avatar_label.setFixedSize(24, 24)

        # Значок типа таска
        task_type_icon = QLabel()
        type_icon = None
        match self.type_name:
            case "Bug":
                type_icon = QIcon(get_resource_path("task_bug_icon.png"))
            case "Story":
                type_icon = QIcon(get_resource_path("task_story_icon.png"))
            case "Task":
                type_icon = QIcon(get_resource_path("task_task_icon.png"))

        type_pixmap = type_icon.pixmap(24, 24)
        task_type_icon.setPixmap(type_pixmap)
        task_type_icon.setFixedSize(30, 30)
        # Текст задачи
        text_label = QLabel(title)
        text_label.setObjectName("TaskText")

        top_layout.addWidget(avatar_label)
        top_layout.addSpacing(8)
        top_layout.addWidget(text_label)
        top_layout.addStretch()
        top_layout.addWidget(task_type_icon)

        wrapper_layout.addLayout(top_layout)

        executor_layout = QHBoxLayout()
        self.executor_label = QLabel(assignee.full_name if assignee else "Не назначен")
        self.executor_label.setStyleSheet("color: #555; font-size: 11px;")
        executor_layout.addWidget(self.executor_label)
        executor_layout.addStretch()

        wrapper_layout.addLayout(executor_layout)

        # Нижняя строка: префикс слева, теги справа
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        # Префикс задачи (например TES-3)
        prefix_label = QLabel(f"{code}")
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
        issue = ServiceOperations.get_issue(0, 0, self.id)
        print('issue', issue)
        """Открытие окна с деталями задачи."""
        details_window = TaskDetailsWindow(
            issue_title=issue.title,
            description=issue.description,
            issue_type=issue.type,
            code=issue.code,
            # issue.avatar_path,
            tags=issue.tags,
            # issue.is_important,
            start_datetime=issue.created_at,
            end_datetime=issue.deadline,
            executor=self.executor_label.text() if hasattr(self, 'executor_label') else "",
            files=getattr(self, 'files', []),
            parent=self
        )
        details_window.show()
