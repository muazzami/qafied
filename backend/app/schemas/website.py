from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class WebsiteBase(BaseModel):
    name: str
    url: HttpUrl


class WebsiteCreate(WebsiteBase):
    show_feedback_by_default: bool = True


class WebsiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    show_feedback_by_default: Optional[bool] = None


class Website(BaseModel):
    id: int
    workspace_id: int
    name: str
    url: str
    script_key: str
    is_active: bool
    show_feedback_by_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebsiteScript(BaseModel):
    script_tag: str
    instructions: str
