import requests
from typing import Optional


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

    def _headers(self):
        if not self.token:
            raise ValueError("You must log in first.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_all_projects(self):
        url = f"{self.base_url}/projects"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def create_project(self, name: str, code: str):
        url = f"{self.base_url}/projects"
        data = {"projectName": name, "projectCode": code}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def create_board(self, project_id: int, board: str):
        url = f"{self.base_url}/projects/{project_id}/boards"
        data = {"boardName": board}
        response = requests.post(url, json=data, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_board(self, projectId: int, boardId: int):
        url = f"{self.base_url}/projects/{projectId}/boards/{boardId}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_project_id(self, project_id: int):
        url = f"{self.base_url}/projects/{project_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_project_full_info(self, project_id: int):
        url = f"{self.base_url}/projects/{project_id}/full"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def delete_project_url(self, project_id: int):
        url = f"{self.base_url}/projects/{project_id}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id: int):
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def put_user_in_project(self, project_id: int, user_id: int):
        url = f"{self.base_url}/projects/{project_id}/users/{user_id}"
        response = requests.patch(url, headers=self._headers())
        response.raise_for_status()



    # Аналогично можно реализовать методы для users, issues, boards и др.
