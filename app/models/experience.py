from beanie import Document, PydanticObjectId
from datetime import datetime, timezone
from typing import List, Optional
from app.models.user import User

class Experience(Document):
    user_id: PydanticObjectId
    title: str
    company: str
    description: str
    technologies: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "experiences"
        indexes = [
            "title",
        ]