import os
import json
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
        self.projects = {}
        self.task_counters = {}
        self.load_projects()

    def add_project(self, name, board_title="Моя доска"):
        if name not in self.projects:
            self.projects[name] = {
                "tasks": {
                    "To Do": [],
                    "In Progress": [],
                    "Done": []
                },
                "board_title": board_title,
                "next_task_number": 0
            }
            self.save_projects()

            os.makedirs(self.get_project_files_dir(name), exist_ok=True)

    def get_projects(self):
        return list(self.projects.keys())

    def save_projects(self):
        print("[SAVE] Сохраняем все проекты в JSON")
        with open("projects.json", "w", encoding="utf-8") as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)

    def load_projects(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.projects = data
                    else:
                        self.projects = {}
            except Exception as e:
                print(f"Ошибка загрузки проектов: {e}")
                self.projects = {}

    def get_projects_data(self, project_name):
        return self.projects.get(project_name, {"tasks": []})

    def get_next_task_number(self, project_name):
        if project_name not in self.task_counters:
            self.task_counters[project_name] = self._get_max_task_number(project_name) + 1
            print(f"[INIT] Счётчик задач для '{project_name}' установлен в {self.task_counters[project_name]}")
        number = self.task_counters[project_name]
        self.task_counters[project_name] += 1
        print(f"[NEXT] Новый номер задачи для '{project_name}': {number}")
        return number

    def _get_max_task_number(self, project_name):
        project = self.projects.get(project_name, {})
        tasks_by_column = project.get("tasks", {})
        max_number = 0
        for column_tasks in tasks_by_column.values():
            for task in column_tasks:
                number = task.get("number", 0)
                if number > max_number:
                    max_number = number
        return max_number

    def delete_project(self, name):
        if name in self.projects:
            del self.projects[name]
            self.save_projects()

    def get_board_prefix(self, project_name):
        board_title = self.projects.get(project_name, {}).get("board_title", "")
        return board_title[:3].upper()

    def get_project_files_dir(self, project_name):
        base_path = "projects_files"  # папка, где хранятся все файлы проектов
        return os.path.join(base_path, project_name)

    def create_project(self, project_name):
        if project_name in self.projects:
            raise ValueError("Проект с таким именем уже существует")

        self.projects[project_name] = {
            "tasks": {},
            "boards": {}
        }

        # Создаём директорию под файлы проекта
        os.makedirs(self.get_project_files_dir(project_name), exist_ok=True)

        self.save_projects()
