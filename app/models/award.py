from beanie import Document, PydanticObjectId
from datetime import datetime, timezone

class Award(Document):
    user_id: PydanticObjectId
    name: str
    issuer: str
    issue_date: datetime
    description: str
    category: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "awards"
        indexes = [
            "name",
        ]
