from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtCore import QSize, Qt

from ui.utils import get_resource_path, ProjectManager
from ui.kanban_desk.task.task_widget import TaskWidget

def create_task_item(task_name, number, title, tags=None, is_important=False,
                    start_datetime=None, end_datetime=None, executor=""):
    item = QListWidgetItem()
    widget = TaskWidget(
        task_name=task_name,
        number=number,
        avatar_path=get_resource_path("logo-alfabank.svg"),
        title=title,
        tags=tags,
        is_important=is_important,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        executor=executor
    )
    item.setSizeHint(widget.sizeHint())
    item.setData(Qt.UserRole, {
        "task_name": task_name,
        "number": number,
        "avatar_path": get_resource_path("logo-alfabank.svg"),
        "title": title,
        "tags": tags or [],
        "is_important": is_important,
        "start_datetime": start_datetime.toString(Qt.ISODate) if start_datetime else None,
        "end_datetime": end_datetime.toString(Qt.ISODate) if end_datetime else None,
        "executor": executor
    })
    return item, widget