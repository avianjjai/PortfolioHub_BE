from beanie import Document
from datetime import datetime, timezone, timedelta
from typing import Optional
from beanie import PydanticObjectId

class AccessToken(Document):
    """Model to store active access tokens in the database"""
    token: str  # The JWT token string
    user_id: PydanticObjectId  # Reference to the user
    username: str  # Username for quick lookup
    role: str  # User role
    created_at: datetime = datetime.now(timezone.utc)
    expires_at: datetime  # When the token expires
    last_used_at: Optional[datetime] = None  # Track last usage for analytics
    
    class Settings:
        name = "access_tokens"
        indexes = [
            "token",  # Index for fast lookup
            "user_id",  # Index for user-based queries
            "expires_at",  # Index for cleanup of expired tokens
        ]
