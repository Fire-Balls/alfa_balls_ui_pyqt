import os

from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QIcon
from PySide6.QtCore import Qt, QRect


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