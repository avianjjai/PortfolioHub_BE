from beanie import Document
from datetime import datetime, timezone

class TokenBlacklist(Document):
    """Model to store blacklisted JWT tokens"""
    token: str  # The JWT token string
    blacklisted_at: datetime = datetime.now(timezone.utc)
    expires_at: datetime  # When the token would naturally expire
    
    class Settings:
        name = "token_blacklist"
        indexes = [
            "token",  # Index for fast lookup
            "expires_at",  # Index for cleanup of expired tokens
        ]
