from PySide6.QtCore import QDateTime
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox,
    QDateTimeEdit, QComboBox
)
import dateutil.parser as parser

from network.new.operations import ServiceOperations
from ui.utils import get_resource_path


class EditTaskDialog(QDialog):
    def __init__(self, issue_id: int, task_name, description, executor, number,
                 task_type="Task", start_datetime=None, end_datetime=None, parent_board=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование задачи")
        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))
        self.setFixedSize(400, 450)
        self.parent_board = parent_board

        self.issue_id = issue_id
        self.task_name_input = QLineEdit(task_name)
        self.description_input = QTextEdit(description)
        self.executor_input = QComboBox()
        self.executor_input.setObjectName("executor_combo")

        parent_board.parent.update_user_list()
        user_list = parent_board.parent.users_list

        for i in range(user_list.count()):
            item = user_list.item(i)
            self.executor_input.addItem(item.text())
        self.executor_input.setCurrentText(executor)
        self.number_input = QLineEdit(str(number))
        self.task_type_combo = QComboBox()
        self.task_type_combo.setObjectName("QComboTopBar")
        self.task_type_combo.addItem(QIcon(get_resource_path("task_bug_icon.png")),
                                     "Bug")  # Баг. Добавить приход с бека названия типа тасков
        self.task_type_combo.addItem(QIcon(get_resource_path("task_story_icon.png")),
                                     "Story")  # Стори Добавить приход с бека названия типа тасков
        self.task_type_combo.addItem(QIcon(get_resource_path("task_task_icon.png")),
                                     "Task")  # Таск Добавить приход с бека названия типа тасков

        self.task_type_combo.setCurrentText(task_type)

        self.start_datetime_input = QDateTimeEdit(start_datetime or QDateTime.currentDateTime())
        self.end_datetime_input = QDateTimeEdit(end_datetime or QDateTime.currentDateTime().addDays(3))
        self.start_datetime_input.setCalendarPopup(True)
        self.end_datetime_input.setCalendarPopup(True)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название задачи:"))
        layout.addWidget(self.task_name_input)

        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.task_type_combo)

        layout.addWidget(QLabel("Исполнитель:"))
        layout.addWidget(self.executor_input)

        layout.addWidget(QLabel("Дедлайн:"))
        layout.addWidget(self.end_datetime_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.update_issue())
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_updated_data(self):
        return {
            "task_name": self.task_name_input.text(),
            "description": self.description_input.toPlainText(),
            "executor": self.executor_input.currentText(),
            "task_type": self.task_type_combo.currentText(),
            "start_datetime": self.start_datetime_input.dateTime(),
            "end_datetime": self.end_datetime_input.dateTime()
        }

    def update_issue(self):
        data = self.get_updated_data()
        existing_issue = ServiceOperations.get_issue(0, 0, self.issue_id)
        all_users = ServiceOperations.get_project(
            ServiceOperations.get_board(0, self.parent_board.board_id).project_id).users
        executor = data['executor'].split(", Роль:")[0]
        parsed_end_datetime = parser.parse(str(data['end_datetime'].toPython())).isoformat()
        assignee = None
        for user in all_users:
            if user.full_name == executor:
                assignee = user

        ServiceOperations.update_issue(
            project_id=0,
            board_id=0,
            issue_id=self.issue_id,
            title=data['task_name'],
            description=data['description'],
            issue_type=data['task_type'],
            status_id=existing_issue.status.id,
            assignee_id=assignee.id,
            deadline=parsed_end_datetime,
            tags=existing_issue.tags
        )

        full_board = ServiceOperations.get_board(0, self.parent_board.board_id)
        project = ServiceOperations.get_project(full_board.project_id)
        for board in project.boards:
            if board.name == full_board.name:
                self.parent_board.set_project_and_board(project, board)

        self.close()