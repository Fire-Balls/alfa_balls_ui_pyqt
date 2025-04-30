from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import QSize, Qt

from ui.utils import get_resource_path, ProjectManager
from ui.kanban_desk.task.task_widget import TaskWidget

def create_task_item(task_name, number, title, avatar_path=None,  tags: list[str] = None, board_prefix=""):
    if tags is None:
        tags = ["js", "C", "HTTP"]
    if avatar_path is None:
        avatar_path = get_resource_path("user_icon.svg")
    # if board_prefix == "":
    #     board_prefix= ProjectManager.get_board_prefix()


    item = QListWidgetItem()
    item.setSizeHint(QSize(200, 60))

    item.setData(Qt.UserRole, {
        "task_name": task_name,
        "number": number,
        "avatar_path": avatar_path,
        "title": title,
        "tags": tags,
        "board_prefix": board_prefix
    })

    widget = TaskWidget(task_name=task_name, number=number, avatar_path=avatar_path, title=title, tags=tags, board_prefix=board_prefix)
    return item, widget