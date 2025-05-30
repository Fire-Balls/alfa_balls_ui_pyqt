from typing import Optional, List
import requests

from network.new.models import Project, Board, User, Issue, IssueStatus, IssueType
from network.new.parsers import parse_project, parse_user, parse_board, parse_issue  # и парсеры в отдельном модуле


class TaskTrackerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None

    def login(self, email: str, password: str):
        url = f"{self.base_url}/auth/login"
        response = requests.post(url, json={"email": email, "password": password})
        response.raise_for_status()
        tokens = response.json()
        self.token = tokens.get("accessToken")
        print(tokens.get("accessToken"))

    def _headers(self):
        if not self.token:
            raise ValueError("You must log in first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # ===== Projects =====

    def get_all_projects(self) -> List[Project]:
        url = f"{self.base_url}/projects"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return [parse_project(p) for p in response.json()]

    def get_project(self, project_id: int) -> Project:
        url = f"{self.base_url}/projects/{project_id}/full"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_project(response.json())

    def create_project(self, name: str, code: str) -> Project:
        url = f"{self.base_url}/projects"
        data = {"projectName": name, "projectCode": code}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_project(response.json())

    def delete_project(self, project_id: int):
        url = f"{self.base_url}/projects/{project_id}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return response.status_code == 204

    def put_user_in_project(self, project_id: int, user_id: int):
        url = f"{self.base_url}/projects/{project_id}/users/{user_id}"
        response = requests.patch(url, headers=self._headers())
        response.raise_for_status()

    # ===== Boards =====

    def create_board(self, project_id: int, board_name: str) -> Board:
        url = f"{self.base_url}/projects/{project_id}/boards"
        data = {"boardName": board_name}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_board(response.json())

    def get_board(self, project_id: int, board_id: int) -> Board:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_board(response.json())

    # ===== Users =====
    def get_user(self, user_id: int) -> User:
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_user(response.json())

    # ===== Issues =====
    def create_issue(
            self,
            project_id: int,
            board_id: int,
            title: str,
            description: str,
            author_id: int,
            assignee_id: Optional[int],
            deadline: str,
            tags: Optional[List[str]] = None
    ) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues"
        data = {
            "title": title,
            "description": description,
            "authorId": author_id,
            "assigneeId": assignee_id,
            "deadline": deadline,  # строка в формате ISO (например, "2025-04-30T22:34:45")
            "tags": tags or []
        }
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_issue(response.json())

    def get_issue(self, project_id: int, board_id: int, issue_id: int) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues/{issue_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_issue(response.json())

    def update_issue(self, project_id: int, board_id: int, issue_id: int, title: str, description: str,
                     type_id: int, status_id: int,
                     author_id: int, assignee_id: Optional[int],
                     deadline: str, tags: Optional[List[str]] = None
    ) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues/{issue_id}"
        data = {
            "title": title,
            "description": description,
            "authorId": author_id,
            "assigneeId": assignee_id,
            "typeId": type_id,
            "statusId": status_id,
            "deadline": deadline,  # строка в формате ISO (например, "2025-04-30T22:34:45")
            "tags": tags or []
        }
        response = requests.put(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_issue(response.json())

    # ===== Statuses =====
    def create_status(self, name: str, project_id: int, board_id: int):
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/statuses"
        data = {"name": name}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_board(response.json())
