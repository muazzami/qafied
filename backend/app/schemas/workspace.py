from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceMemberInfo(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    role: MemberRole
    joined_at: datetime

    class Config:
        from_attributes = True


class Workspace(WorkspaceBase):
    id: int
    slug: str
    owner_id: int
    max_members: int
    is_active: bool
    created_at: datetime
    members: List[WorkspaceMemberInfo] = []

    class Config:
        from_attributes = True


class WorkspaceInvite(BaseModel):
    email: str
    role: MemberRole = MemberRole.MEMBER


class WorkspaceMemberUpdate(BaseModel):
    role: MemberRole
