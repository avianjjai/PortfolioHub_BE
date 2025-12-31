from beanie import Document, PydanticObjectId
from datetime import datetime, timezone, date
from typing import List, Optional

class Project(Document):
    user_id: PydanticObjectId
    title: str
    description: str
    technologies: List[str]
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "projects"
        indexes = [
            "title",
        ]