import os
import subprocess
import sys

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QHBoxLayout,
                               QDialogButtonBox, QFrame, QPushButton, QMessageBox)
from PySide6.QtCore import QDateTime


class TaskDetailsWindow(QDialog):
    """Окно с детальной информацией о задаче."""

    def __init__(self, task_name,description, number, avatar_path=None, tags=None,
                 is_important=False, start_datetime=None, end_datetime=None, executor="", parent=None, files=None):
        super().__init__(parent)

        self.setWindowTitle("Детали задачи")
        self.setFixedSize(450, 500)
        self.task_name = task_name
        self.description = description
        self.executor = executor
        self.number = number
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
        container_layout.addWidget(QLabel(f"<b>Исполнитель:</b> {self.executor}"))
        container_layout.addWidget(QLabel(f"<b>Номер:</b> {self.number}"))

        # Даты
        dates_layout = QVBoxLayout()
        dates_layout.addWidget(QLabel(f"<b>Начало:</b> {self.start_datetime.strftime('%d.%m.%Y %H:%M')}"))#self.start_datetime.toString('dd.MM.yyyy HH:mm')}"))
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
            files_frame = QFrame()
            files_layout = QVBoxLayout(files_frame)
            files_layout.addWidget(QLabel("<b>Прикрепленные файлы:</b>"))

            for file_path in files:
                if os.path.exists(file_path):
                    btn = QPushButton(os.path.basename(file_path))
                    btn.setStyleSheet("""
                                QPushButton {
                                    text-align: left;
                                    padding: 5px;
                                    border: 1px solid #ddd;
                                    border-radius: 3px;
                                }
                                QPushButton:hover {
                                    background-color: #f0f0f0;
                                }
                            """)
                    btn.clicked.connect(lambda _, f=file_path: self.open_file(f))
                    files_layout.addWidget(btn)
                else:
                    # Показываем серым, если файл не найден
                    label = QLabel(f"{os.path.basename(file_path)} (файл отсутствует)")
                    label.setStyleSheet("color: #999;")
                    files_layout.addWidget(label)

            container_layout.addWidget(files_frame)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        container_layout.addWidget(button_box)

    def open_file(self, path):
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])
        else:
            QMessageBox.warning(self, "Ошибка", "Файл не найден")