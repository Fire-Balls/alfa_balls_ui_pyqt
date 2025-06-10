from typing import Optional, List

# from network.new.main import client
# from ui.auth_window.auth_win import client
from network.new.models import Project, Board, User, Issue, IssueType, IssueStatus
from network.new.client_manage import ClientManager


class ServiceOperations:
    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        print("get user")
        client = ClientManager().client
        return client.get_user(user_id)

    @staticmethod
    def update_user(user_id: int, full_name:str, email:str, abs_file_path: str, role: str) -> Optional[User]:
        print("get user")
        client = ClientManager().client
        return client.update_user(user_id, full_name, email, abs_file_path, role)

    @staticmethod
    def create_new_project_with_board(project_name: str, board_name: str):
        client = ClientManager().client
        print("add pr and br")
        saved_project = client.create_project(project_name, "TES")
        project_id = saved_project.id
        client.put_user_in_project(project_id, 1)
        client.create_board(project_id, board_name)

    @staticmethod
    def get_project(project_id: int) -> Optional[Project]:
        client = ClientManager().client
        print("get pr")
        return client.get_project(project_id)

    @staticmethod
    def delete_project(project_id: int):
        client = ClientManager().client
        client.delete_project(project_id)

    @staticmethod
    def get_all_projects_by_user(user_id: int) -> List[Project]:
        client = ClientManager().client
        print("get pr by user")
        return client.get_user(user_id).projects

    @staticmethod
    def create_new_board(project_id: int, board_name: str) -> Board:
        client = ClientManager().client
        print("add new br")
        return client.create_board(project_id, board_name)

    @staticmethod
    def get_board(project_id: int, board_id: int) -> Board:
        client = ClientManager().client
        print("get br")
        board = client.get_board(project_id, board_id)
        return board

    @staticmethod
    def get_project_by_name(project_name: str, user_id: int) -> Optional[Project]:
        for project in ServiceOperations.get_all_projects_by_user(user_id):
            if project.name == project_name:
                return project
        return None

    @staticmethod
    def create_new_issue(project_id: int, board_id: int, title: str, description: str,
                         author_id: int, assignee_id: Optional[int],
                         deadline: str, tags: Optional[List[str]] = None
                         ) -> Issue:
        client = ClientManager().client
        print("issue created")
        return client.create_issue(project_id, board_id, title, description, author_id, assignee_id, deadline, tags)

    @staticmethod
    def get_issue(project_id: int, board_id: int, issue_id: int) -> Issue:
        client = ClientManager().client
        return client.get_issue(project_id, board_id, issue_id)

    @staticmethod
    def create_new_status(name: str, project_id: int, board_id: int):
        client = ClientManager().client
        return client.create_status(name, project_id, board_id)

    @staticmethod
    def update_issue(project_id: int, board_id: int, issue_id: int, title: str, description: str, code: str,
                     type_id: int, status_id: int,
                     author_id: int, assignee_id: Optional[int],
                     deadline: str, tags: Optional[List[str]] = None
                     ) -> Issue:
        print("issue updated")
        client = ClientManager().client
        return client.update_issue(project_id, board_id, issue_id, title, description, code,
                                   type_id, status_id,
                                   author_id, assignee_id,
                                   deadline, tags)

    @staticmethod
    def get_status(project_id: int, board_id: int, status_id: int):
        client = ClientManager().client
        return client.get_status(project_id, board_id, status_id)

    # @staticmethod
    # def get_project_names() -> list[str]:
    #     return [project.name for project in self._projects.values()]
    #
    # @staticmethod
    # def get_by_name(name: str) -> Optional[Project]:
    #     for project in self._projects.values():
    #         if project.name == name:
    #             return project
    #     return None
