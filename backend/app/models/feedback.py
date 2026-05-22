import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FeedbackType(str, enum.Enum):
    CHANGE = "change"
    REMOVE = "remove"
    REPLACE = "replace"
    BUG = "bug"
    SUGGESTION = "suggestion"
    OTHER = "other"


class FeedbackStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    page_url = Column(String, nullable=False)

    commenter_name = Column(String, nullable=True)
    commenter_email = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=True)
    session_id = Column(String, nullable=False)

    content = Column(Text, nullable=False)
    feedback_type = Column(Enum(FeedbackType), default=FeedbackType.SUGGESTION)
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.NEW)

    element_selector = Column(String, nullable=True)
    x_position = Column(Float, nullable=True)
    y_position = Column(Float, nullable=True)

    browser_info = Column(JSON, nullable=True)
    os_info = Column(JSON, nullable=True)
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    viewport_width = Column(Integer, nullable=True)
    viewport_height = Column(Integer, nullable=True)

    include_screenshot = Column(Boolean, default=True)
    screenshot_path = Column(String, nullable=True)

    admin_response = Column(Text, nullable=True)
    responded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    website = relationship("Website", back_populates="feedback_items")
