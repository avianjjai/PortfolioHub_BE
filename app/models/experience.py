from beanie import Document, PydanticObjectId
from datetime import datetime, timezone, date
from typing import List, Optional
from app.models.user import User

class Experience(Document):
    user_id: PydanticObjectId
    title: str
    company: str
    description: str
    technologies: List[str]
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "experiences"
        indexes = [
            "title",
        ]