from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.website import Website
from app.schemas.website import (
    Website as WebsiteSchema,
)
from app.schemas.website import (
    WebsiteCreate,
    WebsiteScript,
    WebsiteUpdate,
)
from app.services.website_service import WebsiteService
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/websites", tags=["websites"])


@router.post("/", response_model=WebsiteSchema)
def create_website(
    workspace_id: int,
    website: WebsiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    WorkspaceService.assert_member(db, workspace_id, current_user.id)

    db_website = Website(
        workspace_id=workspace_id,
        name=website.name,
        url=str(website.url),
        show_feedback_by_default=website.show_feedback_by_default,
    )
    db.add(db_website)
    db.commit()
    db.refresh(db_website)
    return db_website


@router.get("/", response_model=List[WebsiteSchema])
def list_websites(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    WorkspaceService.assert_member(db, workspace_id, current_user.id)

    return (
        db.query(Website)
        .filter(Website.workspace_id == workspace_id, Website.is_active == True)
        .all()
    )


@router.get("/{website_id}", response_model=WebsiteSchema)
def get_website(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = WebsiteService.get_or_404(db, website_id)
    WorkspaceService.assert_member(db, website.workspace_id, current_user.id)
    return website


@router.patch("/{website_id}", response_model=WebsiteSchema)
def update_website(
    website_id: int,
    update: WebsiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = WebsiteService.get_or_404(db, website_id)
    WorkspaceService.assert_member(db, website.workspace_id, current_user.id)

    data = update.model_dump(exclude_unset=True)
    if "url" in data and data["url"] is not None:
        data["url"] = str(data["url"])
    for key, value in data.items():
        setattr(website, key, value)
    db.commit()
    db.refresh(website)
    return website


@router.delete("/{website_id}")
def delete_website(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = WebsiteService.get_or_404(db, website_id)
    WorkspaceService.assert_member(db, website.workspace_id, current_user.id)
    website.is_active = False
    db.commit()
    return {"success": True}


@router.get("/{website_id}/script", response_model=WebsiteScript)
def get_script(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = WebsiteService.get_or_404(db, website_id)
    WorkspaceService.assert_member(db, website.workspace_id, current_user.id)

    return WebsiteScript(
        script_tag=WebsiteService.build_script_tag(website.script_key),
        instructions="Add this script tag to the <head> section of your website.",
    )
