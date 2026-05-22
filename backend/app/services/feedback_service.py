import base64
import os
import uuid
from pathlib import Path
from typing import Optional


SCREENSHOT_DIR = Path(os.getenv("SCREENSHOT_DIR", "/app/screenshots"))


def _decode_data_url(data: str) -> bytes:
    """Accept either a raw base64 string or a data: URL and return raw bytes."""
    if "," in data and data.lstrip().startswith("data:"):
        data = data.split(",", 1)[1]
    return base64.b64decode(data)


class FeedbackService:
    @staticmethod
    def save_screenshot(screenshot_data: Optional[str]) -> Optional[str]:
        """Decode base64 image and write to disk. Returns the relative path or None."""
        if not screenshot_data:
            return None
        try:
            raw = _decode_data_url(screenshot_data)
        except Exception:
            return None

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.png"
        (SCREENSHOT_DIR / filename).write_bytes(raw)
        return f"screenshots/{filename}"
