from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from network.new.models import IssueType
from ui.kanban_desk.task.task_widget import TaskWidget
from ui.utils import get_resource_path


def create_task_item(issue_id, number, title, issue_type: IssueType, executor, tags=None, is_important=False,
                     #task_name, number, description,start_datetime=None, end_datetime=None,
                     ):
    item = QListWidgetItem()
    widget = TaskWidget(
        issue_id=issue_id,
        # description=description,
        code=number,
        # avatar_path=get_resource_path("logo-alfabank.svg"),
        issue_type=issue_type,
        title=title,
        tags=tags,
        is_important=is_important,
        # start_datetime=start_datetime,
        # end_datetime=end_datetime,
        assignee=executor
    )
    item.setSizeHint(widget.sizeHint())
    item.setData(Qt.UserRole, {
        # "task_name": task_name,
        # "description": description,
        'id': issue_id,
        "number": number,
        # "avatar_path": get_resource_path("logo-alfabank.svg"),
        "title": title,
        "tags": tags or [],
        "is_important": is_important,
        # "start_datetime": start_datetime.toString(Qt.ISODate) if start_datetime else None,
        # "end_datetime": end_datetime.toString(Qt.ISODate) if end_datetime else None,
        "executor": executor
    })
    return item, widget
