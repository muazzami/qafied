from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace as WorkspaceModel
from app.models.workspace_member import MemberRole as MemberRoleModel
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import (
    Workspace,
    WorkspaceCreate,
    WorkspaceInvite,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/", response_model=Workspace)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ws = WorkspaceService.create_workspace(
        db, workspace.name, workspace.description, current_user.id
    )
    return WorkspaceService.build_workspace_response(db, ws)


@router.get("/", response_model=List[Workspace])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspaces = WorkspaceService.get_user_workspaces(db, current_user.id)
    return [WorkspaceService.build_workspace_response(db, ws) for ws in workspaces]


@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    WorkspaceService.assert_member(db, workspace_id, current_user.id)
    workspace = (
        db.query(WorkspaceModel).filter(WorkspaceModel.id == workspace_id).first()
    )
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceService.build_workspace_response(db, workspace)


@router.post("/{workspace_id}/invite")
def invite_member(
    workspace_id: int,
    invite: WorkspaceInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    WorkspaceService.assert_member(db, workspace_id, current_user.id)
    member = WorkspaceService.invite_member(
        db,
        workspace_id,
        invite.email,
        MemberRoleModel(invite.role.value),
        current_user.id,
    )
    return {"success": True, "member_id": member.id}
