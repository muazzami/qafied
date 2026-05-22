from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.feedback import Feedback as FeedbackModel
from app.models.user import User
from app.models.website import Website
from app.schemas.feedback import (
    Feedback as FeedbackSchema,
)
from app.schemas.feedback import (
    FeedbackResponse,
    FeedbackStatus,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _assert_website_access(db: Session, website_id: int, user_id: int) -> Website:
    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    WorkspaceService.assert_member(db, website.workspace_id, user_id)
    return website


@router.get("/", response_model=List[FeedbackSchema])
def list_feedback(
    website_id: int,
    page_url: Optional[str] = None,
    status: Optional[FeedbackStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _assert_website_access(db, website_id, current_user.id)

    query = db.query(FeedbackModel).filter(FeedbackModel.website_id == website_id)
    if page_url:
        query = query.filter(FeedbackModel.page_url == page_url)
    if status:
        query = query.filter(FeedbackModel.status == status)

    return query.order_by(FeedbackModel.created_at.desc()).all()


@router.get("/grouped")
def get_grouped_feedback(
    website_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _assert_website_access(db, website_id, current_user.id)

    items = (
        db.query(FeedbackModel)
        .filter(FeedbackModel.website_id == website_id)
        .order_by(FeedbackModel.created_at.desc())
        .all()
    )

    grouped: dict[str, list[FeedbackModel]] = {}
    for item in items:
        grouped.setdefault(item.page_url, []).append(item)

    return [
        {"page_url": url, "count": len(items), "items": items}
        for url, items in grouped.items()
    ]


@router.patch("/{feedback_id}/status")
def update_status(
    feedback_id: int,
    status: FeedbackStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feedback = (
        db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    _assert_website_access(db, feedback.website_id, current_user.id)

    feedback.status = status
    db.commit()
    return {"success": True}


@router.post("/{feedback_id}/response")
def add_response(
    feedback_id: int,
    response: FeedbackResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    feedback = (
        db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    _assert_website_access(db, feedback.website_id, current_user.id)

    feedback.admin_response = response.admin_response
    feedback.responded_by = current_user.id
    feedback.responded_at = datetime.now(timezone.utc)
    db.commit()
    return {"success": True}
