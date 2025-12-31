from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from beanie import PydanticObjectId


class MessageCreatedByAuthenticatedUser(BaseModel):
    messageSubject: Optional[str] = None  # Optional subject, will use default if not provided
    messageContent: str
    recipientEmail: EmailStr

class MessageCreatedByUnauthenticatedUser(BaseModel):
    senderName: str
    senderEmail: EmailStr
    messageSubject: Optional[str] = None  # Optional subject, will use default if not provided
    messageContent: str
    recipientUserId: PydanticObjectId # Portfolio owner's user ID who receives the message

class MessageCreatedResponse(BaseModel):
    id: PydanticObjectId

class MessageResponse(BaseModel):
    id: PydanticObjectId
    conversationId: PydanticObjectId # Conversation ID to group related messages (required)
    senderName: str
    senderEmail: EmailStr
    senderUserId: Optional[PydanticObjectId] = None # Sender's user ID (if authenticated)
    recipientUserId: PydanticObjectId # Portfolio owner's user ID who receives the message
    recipientEmail: Optional[EmailStr] = None
    recipientName: Optional[str] = None
    messageSubject: Optional[str] = None  # Optional subject
    messageContent: str
    created_at: datetime = Field(description="UTC timestamp")
    isRead: bool
    updated_at: datetime = Field(description="UTC timestamp")

class MessageCountResponse(BaseModel):
    read: int
    unread: int
    total: int

class ReadMessageBody(BaseModel):
    messageIds: List[PydanticObjectId] = Field(description="List of message IDs to mark as read")