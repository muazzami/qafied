import secrets

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


def generate_script_key() -> str:
    return secrets.token_urlsafe(32)


class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    script_key = Column(String, unique=True, default=generate_script_key)
    is_active = Column(Boolean, default=True)
    show_feedback_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="websites")
    feedback_items = relationship("Feedback", back_populates="website")
