# import os
# import shutil
# import subprocess
# import sys
#
# from PySide6.QtCore import QModelIndex, QDir, QUrl
# from PySide6.QtGui import QDesktopServices
# from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QFileSystemModel,
#                                QPushButton, QHBoxLayout, QMessageBox, QFileDialog)
#
#
#
# class FolderWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.project_manager = project_manager
#         self.current_project = None
#
#         self.setWindowTitle("Файлы проекта")
#         self.setMinimumSize(600, 400)
#
#         # Модель файловой системы (скрываем системные элементы)
#         self.model = QFileSystemModel()
#         self.model.setRootPath("")
#         self.model.setNameFilterDisables(False)
#
#         # Дерево файлов
#         self.tree = QTreeView()
#         self.tree.setModel(self.model)
#         self.tree.doubleClicked.connect(self.open_file)
#         self.tree.setHeaderHidden(True)
#         self.tree.setColumnHidden(1, True)  # Скрываем колонки Size и Type
#         self.tree.setColumnHidden(2, True)
#         self.tree.setColumnHidden(3, True)
#
#         # Кнопки управления
#         self.btn_add = QPushButton("Добавить файл")
#         self.btn_add.clicked.connect(self.add_file)
#         self.btn_delete = QPushButton("Удалить")
#         self.btn_delete.clicked.connect(self.delete_file)
#         self.btn_refresh = QPushButton("Обновить")
#         self.btn_refresh.clicked.connect(self.refresh)
#
#         # Layout
#         btn_layout = QHBoxLayout()
#         btn_layout.addWidget(self.btn_add)
#         btn_layout.addWidget(self.btn_delete)
#         btn_layout.addWidget(self.btn_refresh)
#
#         main_layout = QVBoxLayout()
#         main_layout.addLayout(btn_layout)
#         main_layout.addWidget(self.tree)
#
#         self.setLayout(main_layout)
#
#     # def set_project(self, project_name):
#     #     self.current_project = project_name
#     #     if project_name:
#     #         project_dir = self.project_manager.get_project_files_dir(project_name)
#     #         os.makedirs(project_dir, exist_ok=True)
#     #
#     #         self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
#     #         self.model.setRootPath(project_dir)
#     #
#     #         index = self.model.index(project_dir)
#     #         self.tree.setRootIndex(index)
#
#     def add_file(self):
#         """Добавляет файлы в папку проекта"""
#         if not self.current_project:
#             return
#
#         files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы")
#         project_dir = self.project_manager.get_project_files_dir(self.current_project)
#
#         for file_path in files:
#             try:
#                 file_name = os.path.basename(file_path)
#                 dest = os.path.join(project_dir, file_name)
#
#                 # Проверка на существование файла
#                 if os.path.exists(dest):
#                     reply = QMessageBox.question(
#                         self,
#                         "Файл существует",
#                         f"Файл {file_name} уже существует. Перезаписать?",
#                         QMessageBox.Yes | QMessageBox.No
#                     )
#                     if reply == QMessageBox.No:
#                         continue
#
#                 shutil.copy(file_path, dest)
#             except Exception as e:
#                 QMessageBox.critical(self, "Ошибка", f"Не удалось добавить файл: {str(e)}")
#
#         self.refresh()
#
#     def delete_file(self):
#         """Удаляет выбранный файл"""
#         index = self.tree.currentIndex()
#         if index.isValid():
#             file_path = self.model.filePath(index)
#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                 elif os.path.isdir(file_path):
#                     shutil.rmtree(file_path)
#                 self.refresh()
#             except Exception as e:
#                 QMessageBox.critical(self, "Ошибка", f"Не удалось удалить: {str(e)}")
#
#     def refresh(self):
#         """Обновляет отображение файлов"""
#         if self.current_project:
#             self.set_project(self.current_project)
#
#     def open_file(self, index):
#         file_path = self.model.filePath(index)
#         QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))