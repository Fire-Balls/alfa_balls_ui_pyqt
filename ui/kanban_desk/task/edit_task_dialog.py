from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox,
    QHBoxLayout, QDateTimeEdit, QComboBox
)
from PySide6.QtCore import QDateTime

from ui.utils import get_resource_path


class EditTaskDialog(QDialog):
    def __init__(self, task_name, description, executor, number,
                 task_type="Task", start_datetime=None, end_datetime=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование задачи")
        self.setWindowIcon(QIcon(get_resource_path("logo-alfabank.svg")))
        self.setFixedSize(400, 450)

        self.task_name_input = QLineEdit(task_name)
        self.description_input = QTextEdit(description)
        self.executor_input = QComboBox()
        self.executor_input.setObjectName("executor_combo")
        user_list_test = ["Roman", "Andry", "Antonio", "Jorik", "Legenda740", "Legenda741", "Legenda742", "Legenda743",
                          "Legenda744", "Legenda745", "Legenda746", "Legenda747", "Legenda748", "Legenda749", ]
        for i in range(len(user_list_test)):
            self.executor_input.addItem(user_list_test[i])  # заменить распарсеным user.fullname и добавлять по порядку тупо по i user.fullname[i]
        self.executor_input.setCurrentText(executor)
        self.number_input = QLineEdit(str(number))
        self.task_type_combo = QComboBox()
        self.task_type_combo.setObjectName("QComboTopBar")
        self.task_type_combo.addItem(QIcon(get_resource_path("task_bug_icon.png")),"Bug")  # Баг. Добавить приход с бека названия типа тасков
        self.task_type_combo.addItem(QIcon(get_resource_path("task_story_icon.png")),"Story")  # Стори Добавить приход с бека названия типа тасков
        self.task_type_combo.addItem(QIcon(get_resource_path("task_task_icon.png")),"Task")  # Таск Добавить приход с бека названия типа тасков

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
        button_box.accepted.connect(self.accept)
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