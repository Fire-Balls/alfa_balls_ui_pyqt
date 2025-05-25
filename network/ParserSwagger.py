from network.network_test import client


def get_board_id_by_name(board_name, data):
    for board in data["kanbanBoards"]:
        if board["boardName"] == board_name:
            return board["boardId"]
    return None  # Если доска не найдена


def get_project_id_by_name(project_name, projects_list):
    for project in projects_list:
        if project['projectName'] == project_name:
            return project['projectId']
    return None  # или можно вызвать исключение, если проект не найден

def get_names_by_user(user_data):
    project_names = []
    for project in user_data["projects"]:
        project_names.append(project["projectName"])
    return project_names


