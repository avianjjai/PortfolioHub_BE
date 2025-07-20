from beanie import Document
from datetime import datetime, timezone
from app.models.user import User

class Skill(Document):
    user: User
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