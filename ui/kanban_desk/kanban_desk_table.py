from PySide6.QtCore import Qt, QUrl, QSize, QAbstractTableModel
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout,QLineEdit,
                               QTableWidget, QHeaderView, QTableWidgetItem,QVBoxLayout)

class HomeInterface(QFrame):  # Создаем отдельный класс для HomeInterface

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.search_input = QLineEdit(self)
        self.kanban_table = QTableWidget(self)
        self.init_ui()

    def init_ui(self):
        # Поиск
        self.search_input.setPlaceholderText("Поиск...")
        # setFont(self.search_input, 12)

        # Kanban доска (таблица)
        self.kanban_table.setColumnCount(4)  # Пример: To Do, In Progress, Review, Done
        self.kanban_table.setHorizontalHeaderLabels(["To Do", "In Progress", "Review", "Done"])
        self.kanban_table.setRowCount(0)  # Пока нет задач
        self.kanban_table.verticalHeader().setVisible(False) # Скрыть вертикальный хедер
        header = self.kanban_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # Растягивание колонок

        # Пример добавления задачи (вы можете заменить это на загрузку из базы данных)
        self.add_task("Сделать UI", "To Do")
        self.add_task("Проверить код", "In Progress")

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.search_input)
        layout.addWidget(self.kanban_table)
        self.setLayout(layout)

        self.setObjectName("homeInterface") #Устанавливаем имя объекта для стилизации


    def add_task(self, task_name, column):
        row_position = self.kanban_table.rowCount()
        self.kanban_table.insertRow(row_position)
        column_index = self.kanban_table.horizontalHeader().visualIndex(self.get_column_index(column))
        self.kanban_table.setItem(row_position, column_index, QTableWidgetItem(task_name))


    def get_column_index(self, column_name):
        header = self.kanban_table.horizontalHeader()
        model = self.kanban_table.model()
        for i in range(header.count()):
            if model.headerData(i, Qt.Horizontal, Qt.DisplayRole) == column_name:
                return i
        return -1  # Возвращает -1 если столбец не найден
