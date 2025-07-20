from beanie import Document, PydanticObjectId
from app.enums.user import UserRole, UserStatus
from datetime import datetime, timezone

class User(Document):
    username: str
    email: str
    hashed_password: str
    is_active: UserStatus = UserStatus.active
    role: UserRole = UserRole.admin
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "users"
        indexes = [
            "username",
            "email",
        ]