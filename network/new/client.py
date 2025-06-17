import base64
import json
import os
from typing import Optional, List
import requests

from network.new.models import Project, Board, User, Issue, IssueStatus
from network.new.parsers import parse_project, parse_user, parse_board, parse_issue, \
    parse_status  # и парсеры в отдельном модуле


class TaskTrackerClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None

    def login(self, email: str, password: str):
        url = f"{self.base_url}/auth/login"
        try:
            response = requests.post(url, json={"email": email, "password": password})
            response.raise_for_status()
            print(response.raise_for_status(), response.status_code)
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 500:
                # Неверный логин или пароль
                raise ValueError("Неверное имя пользователя или пароль") from http_err
            else:
                raise RuntimeError(f"Ошибка сервера: {response.status_code}") from http_err
        except requests.exceptions.RequestException as err:
            # Ошибка сети или другая ошибка запроса
            raise RuntimeError(f"Ошибка соединения: {err}") from err

        tokens = response.json()
        self.token = tokens.get("accessToken")
        self.user_id = tokens.get("userId")
        print(tokens.get("accessToken"))
        if not self.token:
            raise RuntimeError("Токен не получен от сервера")
        return True

    def logout(self):
        ...

    def _headers(self):
        if not self.token:
            raise ValueError("You must log in first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _headers_file(self):
        if not self.token:
            raise ValueError("You must log in first.")
        return {
            "Authorization": f"Bearer {self.token}",
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

    def put_user_in_project(self, project_id: int, user_id: int, role: str):
        url = f"{self.base_url}/projects/{project_id}/users/{user_id}"
        params = {"role": role}
        response = requests.patch(url, headers=self._headers(), params=params)
        response.raise_for_status()

    def send_invite(self, project_id: int, user_id: int, role: str):
        url = f"{self.base_url}/projects/{project_id}/users/{user_id}/invite/send"
        params = {"role": role}
        response = requests.post(url, headers=self._headers(), params=params)
        response.raise_for_status()

    def delete_user_from_project(self, project_id: int, user_id: int):
        url = f"{self.base_url}/projects/{project_id}/users/{user_id}"
        response = requests.delete(url, headers=self._headers())
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
        #print('get_user', response.json())
        return parse_user(response.json())

    def get_user_by_email(self, email: str) -> User:
        url = f"{self.base_url}/users/by-email"
        params = {'email': email}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        #print('get_user_by_email', response.json())
        return parse_user(response.json())

    def update_user(self, user_id: int, full_name: str, email: str, avatar: str) -> User:
        url = f"{self.base_url}/users/{user_id}"
        data = {"fullName": full_name, "email": email, "avatar": avatar if avatar is not None else ""}
        response = requests.put(url, json=data, headers=self._headers())
        response.raise_for_status()
        #print('update_user', response.json())
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
            files_paths: List[str],
            issue_type: str,
            tags: Optional[List[str]] = None
    ) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues"
        data = {
            "title": title,
            "description": description,
            "authorId": author_id,
            "assigneeId": assignee_id,
            "type": issue_type,
            "deadline": deadline,  # строка в формате ISO (например, "2025-04-30T22:34:45")
            "tags": tags or []
        }
        multipart_files = [('issue', ('issue.json', json.dumps(data), 'application/json'))]

        for path in files_paths:
            with open(path, 'rb') as file:
                file_content = file.read()
                file_name = os.path.basename(path)
                multipart_files.append(
                    ('files', (file_name, file_content))
                )

        response = requests.post(url, files=multipart_files, headers=self._headers_file())
        response.raise_for_status()
        return parse_issue(response.json())

    def get_issue(self, project_id: int, board_id: int, issue_id: int) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues/{issue_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_issue(response.json())

    def update_issue(self, project_id: int, board_id: int, issue_id: int, title: str, description: str,
                     issue_type: str, status_id: int, assignee_id: Optional[int],
                     deadline: str, tags: Optional[List[str]] = None
                     ) -> Issue:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/issues/{issue_id}"
        data = {
            "title": title,
            "description": description,
            "assigneeId": assignee_id,
            "type": issue_type,
            "statusId": status_id,
            "deadline": deadline,  # строка в формате ISO (например, "2025-04-30T22:34:45")
            "tags": tags or []
        }
        response = requests.put(url, json=data, headers=self._headers())
        response.raise_for_status()
        print(response)
        print(response.json())
        return parse_issue(response.json())

    # ===== Statuses =====
    def create_status(self, name: str, project_id: int, board_id: int):
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/statuses"
        data = {"name": name}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return parse_status(response.json())

    def get_status(self, project_id: int, board_id: int, status_id: int) -> IssueStatus:
        url = f"{self.base_url}/projects/{project_id}/boards/{board_id}/statuses/{status_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return parse_status(response.json())
