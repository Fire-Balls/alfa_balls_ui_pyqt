import os

from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt

# Функция для получения пути до папки с картинками resource
def get_resource_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к /ui/
    project_root = os.path.dirname(base_path)                # Путь к корню проекта
    return os.path.join(project_root, "resource", filename)

# Функция для получения круглой аватарки
def get_rounded_avatar(path: str, size: int = 100) -> QPixmap:
    original_pixmap = QPixmap(path).scaled(
        size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
    )

    rounded_pixmap = QPixmap(size, size)
    rounded_pixmap.fill(Qt.transparent)

    painter = QPainter(rounded_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, original_pixmap)
    painter.end()

    return rounded_pixmap