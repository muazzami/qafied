from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import MemberRole, WorkspaceMember


class WorkspaceService:
    @staticmethod
    def create_workspace(
        db: Session, name: str, description: str | None, owner_id: int
    ) -> Workspace:
        base_slug = name.lower().replace(" ", "-")
        slug = base_slug
        counter = 1
        while db.query(Workspace).filter(Workspace.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
            max_members=3,
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=MemberRole.OWNER,
            invited_by=owner_id,
        )
        db.add(member)
        db.commit()
        db.refresh(workspace)

        return workspace

    @staticmethod
    def get_user_workspaces(db: Session, user_id: int) -> List[Workspace]:
        memberships = (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.user_id == user_id)
            .all()
        )
        workspace_ids = [m.workspace_id for m in memberships]
        if not workspace_ids:
            return []
        return (
            db.query(Workspace)
            .filter(Workspace.id.in_(workspace_ids), Workspace.is_active == True)
            .all()
        )

    @staticmethod
    def assert_member(db: Session, workspace_id: int, user_id: int) -> WorkspaceMember:
        member = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .first()
        )
        if not member:
            raise HTTPException(
                status_code=403, detail="Not a member of this workspace"
            )
        return member

    @staticmethod
    def invite_member(
        db: Session,
        workspace_id: int,
        email: str,
        role: MemberRole,
        invited_by: int,
    ) -> WorkspaceMember:
        workspace = (
            db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        member_count = (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id)
            .count()
        )
        if member_count >= workspace.max_members:
            raise HTTPException(
                status_code=400, detail="Workspace member limit reached"
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user.id,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member")

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user.id,
            role=role,
            invited_by=invited_by,
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def build_workspace_response(db: Session, workspace: Workspace) -> dict:
        """Build a response dict that includes member details (full_name/email)."""
        members_rows = (
            db.query(WorkspaceMember, User)
            .join(User, User.id == WorkspaceMember.user_id)
            .filter(WorkspaceMember.workspace_id == workspace.id)
            .all()
        )
        members = [
            {
                "id": m.id,
                "user_id": m.user_id,
                "full_name": u.full_name,
                "email": u.email,
                "role": m.role,
                "joined_at": m.joined_at,
            }
            for m, u in members_rows
        ]
        return {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "slug": workspace.slug,
            "owner_id": workspace.owner_id,
            "max_members": workspace.max_members,
            "is_active": workspace.is_active,
            "created_at": workspace.created_at,
            "members": members,
        }
