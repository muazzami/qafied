import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import Feedback
from app.models.website import Website
from app.schemas.feedback import FeedbackCreate
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/widget", tags=["widget"])


@router.get("/config")
def get_widget_config(key: str, db: Session = Depends(get_db)):
    website = (
        db.query(Website)
        .filter(Website.script_key == key, Website.is_active == True)
        .first()
    )
    if not website:
        raise HTTPException(status_code=404, detail="Invalid key")

    return {
        "website_id": website.id,
        "show_by_default": website.show_feedback_by_default,
        "enabled": True,
    }


@router.post("/feedback")
def submit_feedback(
    key: str,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
):
    website = (
        db.query(Website)
        .filter(Website.script_key == key, Website.is_active == True)
        .first()
    )
    if not website:
        raise HTTPException(status_code=404, detail="Invalid key")

    screenshot_path = (
        FeedbackService.save_screenshot(feedback.screenshot_data)
        if feedback.include_screenshot
        else None
    )

    db_feedback = Feedback(
        website_id=website.id,
        page_url=feedback.page_url,
        content=feedback.content,
        feedback_type=feedback.feedback_type,
        commenter_name=feedback.commenter_name,
        commenter_email=feedback.commenter_email,
        is_anonymous=not (feedback.commenter_name or feedback.commenter_email),
        session_id=str(uuid.uuid4()),
        element_selector=feedback.element_selector,
        x_position=feedback.x_position,
        y_position=feedback.y_position,
        browser_info=feedback.browser_info.model_dump() if feedback.browser_info else None,
        os_info=feedback.os_info.model_dump() if feedback.os_info else None,
        screen_width=feedback.screen_width,
        screen_height=feedback.screen_height,
        viewport_width=feedback.viewport_width,
        viewport_height=feedback.viewport_height,
        include_screenshot=feedback.include_screenshot,
        screenshot_path=screenshot_path,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return {"success": True, "feedback_id": db_feedback.id}
