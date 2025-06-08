from datetime import datetime

from network.new.models import Board, Project, User, IssueStatus, IssueType, Issue, ProjectShortcut, IssueShortcut, \
    BoardShortcut


def parse_project_shortcut(data: dict) -> ProjectShortcut:
    return ProjectShortcut(
        id=data['projectId'],
        name=data['projectName'],
        code=data['projectCode']
    )


def parse_user(data: dict) -> User:
    return User(
        id=data['id'],
        full_name=data['fullName'],
        email=data['email'],
        avatar=data['avatar'],
        role =data['role'],
        projects=[parse_project_shortcut(p) for p in data.get('projects', [])]
    )


def parse_status(data: dict) -> IssueStatus:
    return IssueStatus(id=data['id'], name=data['name'], common=data['common'])


def parse_issue_type(data: dict) -> IssueType:
    return IssueType(id=data['id'], name=data['name'], common=data['common'])


def parse_issue(data: dict) -> Issue:
    return Issue(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        type=parse_issue_type(data['type']),
        status=parse_status(data['status']),
        assignee=parse_user(data["assignee"]) if data.get("assignee") else None,
        author=parse_user(data["author"]),
        code=data["code"],
        tags=data.get("tags", []),
        created_at=datetime.fromisoformat(data['createdAt']),
        deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
    )


def parse_issue_shortcut(data: dict) -> IssueShortcut:
    return IssueShortcut(
        id=data["id"],
        title=data["title"],
        type=parse_issue_type(data['type']),
        status=parse_status(data['status']),
        assignee=parse_user(data["assignee"]) if data.get("assignee") else None,
        code=data["code"],
        tags=data.get("tags", []),
    )


def parse_board(data: dict) -> Board:
    return Board(
        id=data['boardId'],
        name=data['boardName'],
        project_id=data['project']['projectId'],
        issues=[parse_issue_shortcut(i) for i in data.get('issues', [])],
        statuses=[parse_status(s) for s in data.get('statuses', [])]
    )


def parse_board_shortcut(data: dict) -> BoardShortcut:
    return BoardShortcut(
        id=data['boardId'],
        name=data['boardName'],
        issues_count=data['issuesCount']
    )


def parse_project(data: dict) -> Project:
    return Project(
        id=data['projectId'],
        name=data['projectName'],
        code=data['projectCode'],
        users=[parse_user(u) for u in data.get('participants', [])],
        # files=[
        #    ProjectFile(id=f['id'], file=f['file'], added_at=datetime.fromisoformat(f['addedAt']))
        #    for f in data.get('files', [])
        # ],
        issue_types=[parse_issue_type(t) for t in data.get('issueTypes', [])],
        boards=[parse_board_shortcut(b) for b in data.get('kanbanBoards', [])]
    )
