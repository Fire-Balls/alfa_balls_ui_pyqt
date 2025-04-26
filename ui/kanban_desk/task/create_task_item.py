from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import QSize, Qt

from ui.utils import get_resource_path
from ui.kanban_desk.task.task_widget import TaskWidget

def create_task_item(task_name, number, tags=None, avatar_path=None):
    if tags is None:
        tags = ["js", "C", "HTTP"]
    if avatar_path is None:
        avatar_path = get_resource_path("logo-alfabank.svg")

    item = QListWidgetItem()
    item.setSizeHint(QSize(200, 60))

    item.setData(Qt.UserRole, {
        "task_name": task_name,
        "number": number,
        "avatar_path": avatar_path,
        "tags": tags
    })

    widget = TaskWidget(task_name=task_name, number=number, avatar_path=avatar_path, tags=tags)
    return item, widget