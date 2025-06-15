import os.path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                               QHBoxLayout, QCheckBox, QDateEdit, QTimeEdit, QComboBox, QListWidget, QFileDialog)
from PySide6.QtCore import QDateTime

from ui.utils import get_resource_path


class AddTaskDialog(QDialog):
    def __init__(self, users_list: QListWidget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить задачу")
        self.setFixedSize(350, 500)
        # Основные поля
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Название задачи")

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Описание задачи")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Теги (через запятую)")

        # Чекбокс для красной рамки
        self.important_checkbox = QCheckBox("Важная задача")
        self.important_checkbox.setChecked(False)

        # Поля для дедлайна
        deadline_layout = QVBoxLayout()

        # # Дата и время начала
        # start_layout = QHBoxLayout()
        # start_layout.addWidget(QLabel("Начало:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDateTime.currentDateTime().date())
        # start_layout.addWidget(self.start_date)
        #
        self.start_time = QTimeEdit()
        self.start_time.setTime(QDateTime.currentDateTime().time())
        # start_layout.addWidget(self.start_time)
        # deadline_layout.addLayout(start_layout)

        # Дата и время окончания
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Дедлайн:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDateTime.currentDateTime().addDays(3).date())
        end_layout.addWidget(self.end_date)

        self.end_time = QTimeEdit()
        self.end_time.setTime(QDateTime.currentDateTime().time())
        end_layout.addWidget(self.end_time)
        deadline_layout.addLayout(end_layout)
        self.executor_combo = QComboBox()
        self.executor_combo.setObjectName("executor_combo")
        self.executor_combo.setEditable(True)  # Разрешаем ручной ввод
        # Тестовый список пользователй убрать после реализации

        for i in range(users_list.count()):
            item = users_list.item(i)
            self.executor_combo.addItem(item.text())
        self.executor_combo.setCurrentIndex(-1)  # Начальное состояние - пустое

        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(100)

        self.btn_add_files = QPushButton("Добавить файлы")
        self.btn_add_files.clicked.connect(self.add_files)

        self.btn_remove_file = QPushButton("Удалить выбранный")
        self.btn_remove_file.clicked.connect(self.remove_file)
        # Кнопка добавления
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.accept)

        # Выбор типа задачи через выпадающий список
        self.task_type_selector = QComboBox()
        self.task_type_selector.setObjectName("QComboTopBar")
        self.task_type_selector.addItem(QIcon(get_resource_path("task_bug_icon.png")), "Bug") # Баг. Добавить приход с бека названия типа тасков
        self.task_type_selector.addItem(QIcon(get_resource_path("task_story_icon.png")), "Story") # Стори Добавить приход с бека названия типа тасков
        self.task_type_selector.addItem(QIcon(get_resource_path("task_task_icon.png")), "Task") # Таск Добавить приход с бека названия типа тасков


        files_layout = QVBoxLayout()
        files_layout.addWidget(QLabel("Прикрепленные файлы:"))
        files_layout.addWidget(self.file_list)
        btn_files_layout = QHBoxLayout()
        btn_files_layout.addWidget(self.btn_add_files)
        btn_files_layout.addWidget(self.btn_remove_file)
        files_layout.addLayout(btn_files_layout)
        # Основной layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название задачи:"))
        layout.addWidget(self.task_name_input)
        layout.addWidget(QLabel("Описание задачи:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Тип задачи:"))
        layout.addWidget(self.task_type_selector)
        layout.addWidget(QLabel("Теги:"))
        layout.addWidget(self.tags_input)
        layout.addWidget(self.important_checkbox)
        layout.addLayout(deadline_layout)
        layout.addWidget(QLabel("Исполнитель:"))
        layout.addWidget(self.executor_combo)
        layout.addLayout(files_layout)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def get_data(self):
        name = self.task_name_input.text().strip()
        description = self.description_input.text().strip()
        tags = [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()]
        is_important = self.important_checkbox.isChecked()
        start_datetime = QDateTime(
            self.start_date.date(),
            self.start_time.time()
        )
        end_datetime = QDateTime(
            self.end_date.date(),
            self.end_time.time()
        )
        executor = self.executor_combo.currentText()
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        issue_type = self.task_type_selector.currentText()
        return name, description, tags, is_important, start_datetime, end_datetime, executor, files, issue_type

    def add_files(self):
        """Добавляет файлы в список"""
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы")
        for file in files:
            self.file_list.addItem(file)

    def remove_file(self):
        """Удаляет выбранный файл из списка"""
        current_item = self.file_list.currentItem()
        if current_item:
            self.file_list.takeItem(self.file_list.row(current_item))
