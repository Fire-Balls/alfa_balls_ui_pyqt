from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ProjectShortcut:
    id: str
    name: str
    code: str


@dataclass
class User:
    id: int
    full_name: str
    email: str
    avatar: str
    projects: List[ProjectShortcut] = field(default_factory=list)


@dataclass
class IssueType:
    id: int
    name: str
    common: bool


@dataclass
class IssueStatus:
    id: int
    name: str
    common: bool


@dataclass
class Issue:
    id: int
    title: str
    description: str
    type: IssueType
    status: IssueStatus
    assignee: Optional[User]
    author: User
    code: str
    created_at: datetime
    deadline: Optional[datetime]
    tags: List[str] = field(default_factory=list)


@dataclass
class IssueShortcut:
    id: int
    title: str
    type: IssueType
    status: IssueStatus
    assignee: Optional[User]
    code: str
    tags: List[str] = field(default_factory=list)


@dataclass
class Board:
    id: int
    name: str
    project_id: int
    issues: List[IssueShortcut] = field(default_factory=list)
    statuses: List[IssueStatus] = field(default_factory=list)


@dataclass
class ProjectFile:
    id: int
    file: str
    added_at: datetime


@dataclass
class Project:
    id: int
    name: str
    code: str
    users: List[User] = field(default_factory=list)
    files: List[ProjectFile] = field(default_factory=list)
    issue_types: List[IssueType] = field(default_factory=list)
    boards: List[Board] = field(default_factory=list)
