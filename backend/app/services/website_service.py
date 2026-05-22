import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.website import Website


WIDGET_URL = os.getenv("WIDGET_URL", "http://localhost:8080")


class WebsiteService:
    @staticmethod
    def build_script_tag(script_key: str) -> str:
        return f'<script src="{WIDGET_URL}/widget.js" data-key="{script_key}"></script>'

    @staticmethod
    def get_or_404(db: Session, website_id: int) -> Website:
        website = db.query(Website).filter(Website.id == website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        return website
