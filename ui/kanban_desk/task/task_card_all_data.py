import os
import subprocess
import sys
import webbrowser

from PySide6.QtWidgets import QScrollArea

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout,
                               QDialogButtonBox, QFrame, QPushButton, QMessageBox, QWidget)
from PySide6.QtCore import QDateTime, Qt

from ui.kanban_desk.task.edit_task_dialog import EditTaskDialog


class TaskDetailsWindow(QDialog):
    """Окно с детальной информацией о задаче."""

    def __init__(self, issue_title, description, code, issue_type, avatar_path=None, tags=None,
                 is_important=False, start_datetime=None, end_datetime=None, executor="", parent=None, files=None):
        super().__init__(parent)

        self.iterator = 0
        self.setWindowTitle("Детали задачи")
        self.setFixedSize(450, 550)
        self.task_name = issue_title
        self.issue_type = issue_type
        self.description = description
        self.executor = executor
        self.number = code
        self.avatar_path = avatar_path
        self.tags = tags or []
        self.is_important = is_important
        self.start_datetime = start_datetime or QDateTime.currentDateTime()
        self.end_datetime = end_datetime or QDateTime.currentDateTime().addDays(3)

        # Основной контейнер
        container = QFrame()
        container.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px;")

        layout = QVBoxLayout(self)
        layout.addWidget(container)

        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)

        # Информация о задаче
        container_layout.addWidget(QLabel(f"<b>Задача:</b> {self.task_name}"))
        container_layout.addWidget(QLabel(f"<b>Описание:</b> {self.description}"))
        container_layout.addWidget(QLabel(f"<b>Тип задачи:</b> {self.issue_type}"))
        container_layout.addWidget(QLabel(f"<b>Исполнитель:</b> {self.executor}"))
        container_layout.addWidget(QLabel(f"<b>Номер:</b> {self.number}"))

        # Даты
        dates_layout = QVBoxLayout()
        dates_layout.addWidget(QLabel(f"<b>Начало:</b> {self.start_datetime.strftime('%d.%m.%Y %H:%M')}"))
        dates_layout.addWidget(QLabel(f"<b>Дедлайн:</b> {self.end_datetime.strftime('%d.%m.%Y %H:%M')}"))
        container_layout.addLayout(dates_layout)

        # Статус важности
        importance_label = QLabel("<b>Статус:</b> " + ("Важная" if self.is_important else "Обычная"))
        container_layout.addWidget(importance_label)

        # Теги
        if self.tags:
            tags_layout = QHBoxLayout()
            tags_layout.addWidget(QLabel("<b>Теги:</b>"))
            for tag in self.tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("background-color: lightblue; border-radius: 5px; padding: 2px 5px;")
                tags_layout.addWidget(tag_label)
            container_layout.addLayout(tags_layout)
        print(files)
        if files:
            files_scroll = QScrollArea()
            files_scroll.setWidgetResizable(True)
            #files_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            self.setFixedSize(450, 700)

            # Контейнер внутри скролла
            files_frame = QWidget()
            files_layout = QVBoxLayout(files_frame)
            files_layout.addWidget(QLabel("<b>Прикрепленные файлы:</b>"))

            for file_url in files:
                file_name = os.path.basename(file_url)

                link_label = QLabel(f'<a href="{file_url}">{file_name}</a>')
                link_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
                link_label.setOpenExternalLinks(False)
                link_label.setStyleSheet("QLabel { color: #2a8fdb; text-decoration: underline; }")

                # Важно: сохранить ссылку внутри лямбды корректно
                link_label.linkActivated.connect(lambda url=file_url: webbrowser.open(url))

                files_layout.addWidget(link_label)

            files_scroll.setWidget(files_frame)
            container_layout.addWidget(files_scroll)

        # Ссылки на файлы


        # Кнопки
        buttons_layout = QHBoxLayout()
        button_edit = QPushButton("Редактировать")
        button_edit.setFixedSize(140, 40)
        button_edit.clicked.connect(lambda: self.open_edit_window())
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        buttons_layout.addWidget(button_edit)
        buttons_layout.addStretch()
        buttons_layout.addWidget(button_box)
        container_layout.addLayout(buttons_layout)

    def open_edit_window(self):

        dialog = EditTaskDialog(
            task_name=self.task_name,
            description=self.description,
            executor=self.executor,
            number=self.number,
            task_type="Task",  # временно жестко, подставь своё поле
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime
        )

        if dialog.exec():
            updated = dialog.get_updated_data()
            # Пример обновления полей (допиши остальные)
            self.task_name = updated["task_name"]
            self.description = updated["description"]
            self.executor = updated["executor"]
            self.start_datetime = updated["start_datetime"]
            self.end_datetime = updated["end_datetime"]