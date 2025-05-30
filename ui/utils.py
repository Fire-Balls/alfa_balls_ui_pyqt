import os
import json
import shutil

from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from PySide6.QtCore import Qt


# Функция для получения пути до папки с картинками resource
def get_resource_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к /ui/
    project_root = os.path.dirname(base_path)  # Путь к корню проекта
    return os.path.join(project_root, "resource", filename)


# Функция для получения круглой аватарки
def get_rounded_avatar_icon(path: str, size: int = 100) -> QIcon:
    original_pixmap = QPixmap(path)

    # Масштабируем, заполняя весь круг
    scaled = original_pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Создаем пустой прозрачный pixmap
    result = QPixmap(size, size)
    result.fill(Qt.transparent)

    # Рисуем круг
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)

    path_clip = QPainterPath()
    path_clip.addEllipse(0, 0, size, size)
    painter.setClipPath(path_clip)

    # Центрируем изображение внутри круга
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()

    return QIcon(result)


PROJECTS_FILE = "projects.json"


class ProjectManager:
    def __init__(self, file_path=PROJECTS_FILE):
        self.file_path = file_path
#
#     def add_project(self, name, board_title):
#         if name not in self.projects:
#             self.projects[name] = {
#                 "boards": {
#                     board_title: {
#                         "To Do": [],
#                         "In Progress": [],
#                         "Done": []
#                     }
#                 },
#                 "next_task_number": 0
#             }
#             self.save_projects()
#             os.makedirs(self.get_project_files_dir(name), exist_ok=True)
#
#     def add_project_on_server_and_client(self, name, board_title):
#         saved_project = client.create_project(name, "TES")
#         project_id: int = saved_project['projectId']
#         client.put_user_in_project(project_id, 1)
#
#         saved_board = client.create_board(project_id, board_title)
#         # board_id = saved_board['boardId']
#
#         self.add_project(name, board_title)
#
#     def get_projects_from_server(self):
#         self.clear_project_json()
#         for project in ParserSwagger.get_projects_by_user(client.get_user(self.user_id)):
#             project_name = project['projectName']
#             full_project = client.get_project_full_info(project['projectId'])
#
#             if len(full_project["kanbanBoards"]) != 0:
#                 first_board_name = full_project["kanbanBoards"][0]["boardName"]
#             else:
#                 first_board_name = None
#
#             self.add_project(project_name, first_board_name)
#         return self.get_projects()
#
#     def get_projects(self):
#         return list(self.projects.keys())
#
#     def get_default_board(self, project_name):
#         project = self.projects.get(project_name, {})
#         boards = project.get("boards", {})
#         return next(iter(boards.keys()), None)
#
#     def get_boards(self, project_name):
#         return list(self.projects.get(project_name, {}).get("boards", {}).keys())
#
#     def create_board(self, project_name: str, board_name: str):
#         if project_name in self.projects:
#             boards = self.projects[project_name]["boards"]
#             if board_name not in boards:
#                 boards[board_name] = {
#                     "To Do": [],
#                     "In Progress": [],
#                     "Done": []
#                 }
#                 self.projects[project_name]["current_board"] = board_name
#                 self.save_projects()
#
#     def set_current_project(self, name):
#         self.current_project = name
#         self.current_board = next(iter(self.get_boards(name)), None)
#
#     def set_current_board(self, project_name: str, board_name: str):
#         if project_name in self.projects:
#             self.projects[project_name]["current_board"] = board_name
#             self.save_projects()
#
#     def get_tasks(self, project_name: str, board_name: str):
#         project = self.projects.get(project_name, {})
#         boards = project.get("boards", {})
#         return boards.get(board_name, {})
#
#     def save_projects(self):
#         print("[SAVE] Сохраняем все проекты в JSON")
#         with open(self.file_path, "w", encoding="utf-8") as f:
#             json.dump(self.projects, f, ensure_ascii=False, indent=2)
#
#     def load_projects(self):
#         if os.path.exists(self.file_path):
#             try:
#                 with open(self.file_path, "r", encoding="utf-8") as f:
#                     data = json.load(f)
#                     if isinstance(data, dict):
#                         self.projects = data
#                     else:
#                         self.projects = {}
#             except Exception as e:
#                 print(f"Ошибка загрузки проектов: {e}")
#                 self.projects = {}
#
#     def get_next_task_number(self, project_name):
#         if project_name not in self.task_counters:
#             self.task_counters[project_name] = self._get_max_task_number(project_name) + 1
#         number = self.task_counters[project_name]
#         self.task_counters[project_name] += 1
#         return number
#
#     def _get_max_task_number(self, project_name):
#         max_number = 0
#         project = self.projects.get(project_name, {})
#         for board in project.get("boards", {}).values():
#             for column in board.values():
#                 for task in column:
#                     number = task.get("number", 0)
#                     if number > max_number:
#                         max_number = number
#         return max_number
#
#     def delete_project(self, name):
#         if name in self.projects:
#             del self.projects[name]
#             self.save_projects()
#
#     def get_project_files_dir(self, project_name):
#         base_path = "projects_files"
#         return os.path.join(base_path, project_name)
#
#     def delete_folder(self, project_name):
#         base_path = "projects_files"
#         path = os.path.join(base_path, project_name)
#         if os.path.isdir(path):
#             try:
#                 shutil.rmtree(path)
#                 print(f"Папка '{path}' успешно удалена.")
#             except Exception as e:
#                 print(f"Ошибка при удалении папки '{path}': {e}")
#
#     def clear_project_json(self):
#         for project in self.projects:
#             self.delete_folder(project)
#
#         try:
#             with open(self.file_path, 'w', encoding='utf-8') as f:
#                 json.dump({}, f, ensure_ascii=False, indent=4)
#             print(f"Файл '{self.file_path}' успешно очищен (записан пустой JSON-массив).")
#         except Exception as e:
#             print(f"Ошибка при очистке файла '{self.file_path}': {e}")
