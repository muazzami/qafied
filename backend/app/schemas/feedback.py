from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FeedbackType(str, Enum):
    CHANGE = "change"
    REMOVE = "remove"
    REPLACE = "replace"
    BUG = "bug"
    SUGGESTION = "suggestion"
    OTHER = "other"


class FeedbackStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class BrowserInfo(BaseModel):
    name: str
    version: str


class OSInfo(BaseModel):
    name: str
    version: str


class FeedbackCreate(BaseModel):
    page_url: str
    content: str
    feedback_type: FeedbackType = FeedbackType.SUGGESTION
    commenter_name: Optional[str] = None
    commenter_email: Optional[str] = None
    element_selector: Optional[str] = None
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    browser_info: Optional[BrowserInfo] = None
    os_info: Optional[OSInfo] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    include_screenshot: bool = True
    screenshot_data: Optional[str] = None


class FeedbackResponse(BaseModel):
    admin_response: str


class Feedback(BaseModel):
    id: int
    website_id: int
    page_url: str
    commenter_name: Optional[str]
    commenter_email: Optional[str]
    is_anonymous: bool
    content: str
    feedback_type: FeedbackType
    status: FeedbackStatus
    element_selector: Optional[str]
    x_position: Optional[float]
    y_position: Optional[float]
    browser_info: Optional[Dict[str, Any]]
    os_info: Optional[Dict[str, Any]]
    screen_width: Optional[int]
    screen_height: Optional[int]
    viewport_width: Optional[int]
    viewport_height: Optional[int]
    include_screenshot: bool
    screenshot_path: Optional[str]
    admin_response: Optional[str]
    responded_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackGroup(BaseModel):
    page_url: str
    count: int
    feedback_items: List[Feedback]
