from beanie import Document
from datetime import datetime, timezone
from typing import List, Optional
from app.models.user import User

class Experience(Document):
    user: User
    title: str 
    description: str
    technologies: List[str]
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "experiences"
        indexes = [
            "title",
        ]