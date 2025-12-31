from beanie import Document, PydanticObjectId
from datetime import datetime, timezone
from typing import Optional
from pydantic import Field


class Message(Document):
    conversationId: PydanticObjectId  # Conversation ID to group related messages (required)
    senderName: Optional[str] = None
    senderEmail: Optional[str] = None
    senderUserId: Optional[PydanticObjectId] = None  # Sender's user ID (if authenticated)
    recipientUserId: PydanticObjectId
    recipientEmail: Optional[str] = None
    recipientName: Optional[str] = None
    messageSubject: Optional[str] = None  # Optional subject with smart defaults
    messageContent: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    isDeletedForSender: bool = False
    isDeletedForRecipient: bool = False
    isRead: bool = False

    class Settings:
        name = "message"