import os


# Функция для получения пути до папки с картинками resource
def get_resource_path(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к /ui/
    project_root = os.path.dirname(base_path)                # Путь к корню проекта
    return os.path.join(project_root, "resource", filename)