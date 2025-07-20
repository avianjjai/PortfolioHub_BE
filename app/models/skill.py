from beanie import Document, PydanticObjectId
from datetime import datetime, timezone

class Skill(Document):
    user_id: PydanticObjectId
    name: str
    category: str
    proficiency: int
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "skills"
        indexes = [
            "name",
        ]