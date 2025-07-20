from beanie import Document, PydanticObjectId
from datetime import datetime, timezone
from typing import Optional

class Education(Document):
    user_id: PydanticObjectId
    institution: str
    degree: str
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "educations"
        indexes = [
            "institution",
        ]