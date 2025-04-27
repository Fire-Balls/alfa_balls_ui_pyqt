import os
import json
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from PySide6.QtCore import Qt


# Функция для получения пути до папки с картинками resource
def get_resource_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к /ui/
    project_root = os.path.dirname(base_path)                # Путь к корню проекта
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


class ProjectManager:
    def __init__(self, file_path="projects.json"):
        self.file_path = file_path
        self.projects = []
        self.load_projects()

    def add_project(self, name):
        self.projects.append(name)
        self.save_projects()

    def get_projects(self):
        return self.projects

    def save_projects(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.projects, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения проектов: {e}")

    def load_projects(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.projects = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки проектов: {e}")
                self.projects = []