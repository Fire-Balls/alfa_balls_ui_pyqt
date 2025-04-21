import os

from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRect


# Функция для получения пути до папки с картинками resource
def get_resource_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к /ui/
    project_root = os.path.dirname(base_path)                # Путь к корню проекта
    return os.path.join(project_root, "resource", filename)

# Функция для получения круглой аватарки
def get_rounded_avatar(path: str, size: int = 100) -> QPixmap:
    original_pixmap = QPixmap(path)

    # Масштабируем, заполняя весь круг, возможно с обрезкой
    scaled = original_pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Центрируем и обрезаем под круг
    result = QPixmap(size, size)
    result.fill(Qt.transparent)

    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)

    # Обрезка по кругу
    path_clip = QPainterPath()
    path_clip.addEllipse(0, 0, size, size)
    painter.setClipPath(path_clip)

    # Координаты для центрирования
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()

    return result