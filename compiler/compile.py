import os
import PyInstaller.__main__

def compile_project(project_path):
    main_file = os.path.join(project_path, 'start_app.py')
    if not os.path.exists(main_file):
        print(f'Ошибка: Файл main_app.py {main_file} не найден в {project_path}')
        return

    # Папки для исключения
    exclude_folders = {
        '.idea',
        '.venv',
        'venv',
        '__pycache__',
        'polygon',
        'build',
        'dist',
    }

    # Собираем все папки в проекте, исключая указанные
    folders_to_include = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_folders]
        for dir_ in dirs:
            folder_path = os.path.join(root, dir_)
            relative_path = os.path.relpath(str(folder_path), project_path)
            folders_to_include.append(
                f'--add-data={folder_path}{os.pathsep}{relative_path}'
            )

    # Настройки PyInstaller
    pyinstaller_args = [
        '--onefile',
        '--clean',
        '--noconsole',
        '--name=Kanban' ,
        '--exclude-module', 'PyQt6',
        *folders_to_include,
        main_file,
    ]

    # Запуск PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)
    print('Компиляция завершена успешно!')

if __name__ == "__main__":
    PROJECT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
    print(PROJECT_PATH)
    compile_project(PROJECT_PATH)