import sys

from PySide6.QtCore import QModelIndex, QDir, QUrl, Qt, QAbstractItemModel
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QFileSystemModel,
                               QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QApplication)
from network.new.operations import ServiceOperations

class UrlTreeModel(QAbstractItemModel):
    """
    Модель данных для отображения URL-адресов в QTreeView.
    """

    def __init__(self, urls: set = None, parent=None):
        super().__init__(parent)
        self.urls = list(urls) if urls else []  # Преобразуем set в list для индексации

    def rowCount(self, parent=QModelIndex()):
        """
        Возвращает количество строк (URL-адресов) в модели.
        """
        if parent.isValid():
            return 0  # URL-адреса не имеют дочерних элементов
        return len(self.urls)

    def columnCount(self, parent=QModelIndex()):
        """
        Возвращает количество столбцов (только один столбец для URL-адреса).
        """
        return 1

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """
        Возвращает данные для заданного индекса и роли.
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return self.urls[index.row()]  # Возвращаем URL-адрес

        return None

    def index(self, row, column, parent=QModelIndex()):
        """
        Возвращает QModelIndex для заданного ряда, столбца и родительского элемента.
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, None)

    def parent(self, index: QModelIndex):
        """
        Возвращает родительский QModelIndex. В данном случае, у всех URL-адресов нет родителя.
        """
        return QModelIndex()

    def add_urls(self, urls: set):
        """
        Добавляет новые URL-адреса в модель и уведомляет представление об изменениях.
        """
        self.beginResetModel()  # Начинаем операцию сброса модели
        self.urls = list(urls) # Обновляем список URL
        self.endResetModel()  # Завершаем операцию сброса модели и уведомляем представление


class FolderWindow(QWidget):
    def __init__(self, user_id, project_id):
        super().__init__()
        self.user_id = user_id
        self.project_id = project_id
        self.setWindowTitle("Файлы проекта")

        self.setMinimumSize(600, 400)

        # Модель данных для URL-адресов
        self.url_model = UrlTreeModel()

        # Дерево файлов
        self.tree = QTreeView()
        self.tree.setModel(self.url_model)  # Устанавливаем нашу модель
        self.tree.doubleClicked.connect(self.open_url)  # Подключаем сигнал двойного щелчка
        self.tree.setHeaderHidden(True)  # Скрываем заголовки столбцов
        self.refresh()
        # Кнопки управления
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_refresh)

        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.tree)

        self.setLayout(main_layout)

    def set_urls(self, urls: set):
        """
        Устанавливает список URL-адресов в модели.
        """
        self.url_model.add_urls(urls)

    def open_url(self, index: QModelIndex):
        """
        Открывает URL-адрес, соответствующий выбранному индексу.
        """
        url = self.url_model.data(index, Qt.DisplayRole)
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def refresh(self):
        """Обновляет отображение файлов, запрашивая данные с сервера."""
        all_urls = set()
        project_moment = ServiceOperations.get_project(self.project_id)
        if project_moment: # Проверка на None
            for issues in project_moment.issues:
                issue = ServiceOperations.get_issue(self.project_id, project_moment.id, issues.id)
                if issue: # Проверка на None
                    all_urls.update(set(issue.file_urls))
        self.set_urls(all_urls)
