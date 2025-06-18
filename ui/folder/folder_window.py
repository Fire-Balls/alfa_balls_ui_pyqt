import sys
import os
from PySide6.QtCore import QModelIndex, QDir, QUrl, Qt, QAbstractItemModel
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QFileSystemModel, QLabel,QLineEdit,
                               QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QApplication)
from network.new.operations import ServiceOperations
import webbrowser

class UrlTreeModel(QAbstractItemModel):
    """
    Модель данных для отображения URL-адресов в QTreeView с названиями файлов.
    """

    def __init__(self, urls: set = None, parent=None):
        super().__init__(parent)
        self.urls = list(urls) if urls else []  # Преобразуем set в list для индексации
        self.filtered_urls = self.urls[:] # Копия для фильтрации
        self.filter_text = ""

    def rowCount(self, parent=QModelIndex()):
        """
        Возвращает количество строк (URL-адресов) в модели.
        """
        if parent.isValid():
            return 0  # URL-адреса не имеют дочерних элементов
        return len(self.filtered_urls)

    def columnCount(self, parent=QModelIndex()):
        """
        Возвращает количество столбцов (только один столбец для названия файла).
        """
        return 1

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """
        Возвращает данные для заданного индекса и роли.  Возвращает только название файла.
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            url = self.filtered_urls[index.row()]
            return os.path.basename(url)  # Возвращаем только название файла

        if role == Qt.UserRole:  # Возвращаем полный URL для обработки двойного щелчка
            return self.filtered_urls[index.row()]

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
        self.urls = list(urls)  # Обновляем список URL
        self.apply_filter()
        self.endResetModel()  # Завершаем операцию сброса модели и уведомляем представление

    def set_filter(self, text):
        """
        Устанавливает текст фильтра и применяет его.
        """
        self.filter_text = text.lower()
        self.apply_filter()

    def apply_filter(self):
        """
        Применяет фильтр к списку URL-адресов.
        """
        self.beginResetModel()
        if not self.filter_text:
            self.filtered_urls = self.urls[:] # Копия всего списка
        else:
            self.filtered_urls = [url for url in self.urls if self.filter_text in os.path.basename(url).lower()]
        self.endResetModel()



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

        # Поиск
        self.search_field = QLineEdit()
        self.search_field.textChanged.connect(self.filter_urls)

        # Кнопки управления
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_refresh)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("<b>Поиск:</b>"))

        search_layout.addWidget(self.search_field)

        main_layout = QVBoxLayout()
        main_layout.addLayout(search_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.tree)

        self.setLayout(main_layout)

        # Устанавливаем стиль

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

    def open_url(self, index: QModelIndex):
        """
        Открывает URL-адрес, соответствующий выбранному индексу.
        """
        url = self.url_model.data(index, Qt.UserRole)  # Получаем полный URL из UserRole
        if url:
            webbrowser.open(url) # Используем webbrowser.open для открытия в браузере.


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

    def filter_urls(self, text):
        """
        Фильтрует список URL-адресов на основе введенного текста.
        """
        self.url_model.set_filter(text)  # Передаем текст фильтра в модель.
