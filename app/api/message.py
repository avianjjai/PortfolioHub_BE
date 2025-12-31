import re
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.message import Message
from ..schemas.message import MessageCreatedByAuthenticatedUser, MessageCreatedByUnauthenticatedUser, MessageCreatedResponse, MessageResponse, MessageCountResponse, ReadMessageBody
from app.utils.auth import get_current_user
from ..models.user import User
from datetime import datetime, timezone
from beanie import PydanticObjectId
from app.utils.auth import require_role
from app.schemas.error import Error
from app.websocket import manager

router = APIRouter()

def evaluate_message_read_status(messages: List[Message], current_user: User):
    for message in messages:
        message.isRead = message.isRead or message.senderUserId == current_user.id
    return messages


def serialize_message(message: Message) -> dict:
    data = message.model_dump()
    data["id"] = str(message.id)
    data["_id"] = str(message.id)
    data["conversationId"] = str(data["conversationId"])  # conversationId is required
    if data.get("senderUserId"):
        data["senderUserId"] = str(data["senderUserId"])
    if data.get("recipientUserId"):
        data["recipientUserId"] = str(data["recipientUserId"])
    data["created_at"] = message.created_at.isoformat()
    data["updated_at"] = message.updated_at.isoformat()
    return data


async def find_or_create_conversation_id(
    sender_email: str,
    recipient_email: str,
    sender_user_id: Optional[PydanticObjectId] = None,
    recipient_user_id: Optional[PydanticObjectId] = None
) -> PydanticObjectId:
    """
    Find existing conversationId between two participants, or create a new one.
    Looks for messages where participants match (by email or userId).
    Always returns a conversationId.
    """
    # Build query conditions for matching participants
    or_conditions = []
    
    # Match by email addresses (bidirectional)
    or_conditions.append({
        "senderEmail": sender_email,
        "recipientEmail": recipient_email
    })
    or_conditions.append({
        "senderEmail": recipient_email,
        "recipientEmail": sender_email
    })
    
    # If we have user IDs, also match by them (bidirectional)
    if sender_user_id and recipient_user_id:
        or_conditions.append({
            "senderUserId": sender_user_id,
            "recipientUserId": recipient_user_id
        })
        or_conditions.append({
            "senderUserId": recipient_user_id,
            "recipientUserId": sender_user_id
        })
    
    # Find the most recent message in this conversation that has a conversationId
    existing_messages = await Message.find({
        "$and": [
            {"conversationId": {"$ne": None}},  # Only messages with conversationId
            {"$or": or_conditions}
        ]
    }).sort("-created_at").limit(1).to_list()
    
    if existing_messages and len(existing_messages) > 0:
        existing_message = existing_messages[0]
        if existing_message and existing_message.conversationId:
            return existing_message.conversationId
    
    # No existing conversation found, create a new conversationId
    return PydanticObjectId()


async def notify_new_message(message_doc: Message, recipient_user_id: str, sender_user_id: Optional[str] = None):
    payload = {
        "event": "message:new",
        "payload": serialize_message(message_doc)
    }
    await manager.send_personal_message(recipient_user_id, payload)
    if sender_user_id and sender_user_id != recipient_user_id:
        await manager.send_personal_message(sender_user_id, payload)


async def notify_messages_read(message_ids: List[str], user_ids: List[str]):
    payload = {
        "event": "message:read",
        "payload": {
            "messageIds": message_ids
        }
    }
    for user_id in user_ids:
        await manager.send_personal_message(user_id, payload)

@router.post('/send', dependencies=[Depends(require_role("admin"))], response_model=MessageCreatedResponse)
async def message(message: MessageCreatedByAuthenticatedUser, current_user: User = Depends(get_current_user)):
    """Create a new authenticated user message"""
    recipient_user = await User.find_one(User.email == message.recipientEmail)
    if not recipient_user:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message="Recipient user not found", 
                status_code=404
            ).model_dump()
        )
    
    if recipient_user.id == current_user.id:
        raise HTTPException(
            status_code=400, 
            detail=Error(
                message="You cannot send a message to yourself", 
                status_code=400
            ).model_dump()
        )
    
    # Build sender name from user's first and last name, fallback to username
    sender_name = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip()
    if not sender_name:
        sender_name = current_user.username

    # Find or create conversationId (always returns a conversationId)
    conversation_id = await find_or_create_conversation_id(
        sender_email=current_user.email,
        recipient_email=recipient_user.email,
        sender_user_id=current_user.id,
        recipient_user_id=recipient_user.id
    )

    # Use subject from frontend (or None if not provided)
    message_subject = message.messageSubject if message.messageSubject and message.messageSubject.strip() else None

    # Create message with explicit timestamps
    current_time = datetime.now(timezone.utc)
    new_message = {
        **message.model_dump(),
        'conversationId': conversation_id,
        'messageSubject': message_subject,  # Use what frontend provides, or None
        'senderUserId': current_user.id,
        'senderName': sender_name,
        'senderEmail': current_user.email,
        'recipientUserId': recipient_user.id,
        'recipientEmail': recipient_user.email,
        'recipientName': f"{recipient_user.first_name or ''} {recipient_user.last_name or ''}".strip(),
        'created_at': current_time,
        'updated_at': current_time,
    }
    message_created = await Message(**new_message).insert()
    await notify_new_message(message_created, str(recipient_user.id), str(current_user.id))
    return message_created

@router.post('/send/unauthenticated', response_model=MessageCreatedResponse)
async def message(message: MessageCreatedByUnauthenticatedUser):
    """Create a new unauthenticated user message"""
    recipient_user = await User.get(message.recipientUserId)
    if not recipient_user:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message="Recipient user not found", 
                status_code=404
            ).model_dump()
        )
    
    # Find or create conversationId (always returns a conversationId)
    conversation_id = await find_or_create_conversation_id(
        sender_email=message.senderEmail,
        recipient_email=recipient_user.email,
        sender_user_id=None,  # Unauthenticated sender has no userId
        recipient_user_id=recipient_user.id
    )

    # Use subject from frontend (or None if not provided)
    message_subject = message.messageSubject if message.messageSubject and message.messageSubject.strip() else None

    # Create message with explicit timestamps
    current_time = datetime.now(timezone.utc)
    new_message = {
        **message.model_dump(),
        'conversationId': conversation_id,
        'messageSubject': message_subject,  # Use what frontend provides, or None
        'recipientEmail': recipient_user.email,
        'recipientName': f"{recipient_user.first_name or ''} {recipient_user.last_name or ''}".strip(),
        'created_at': current_time,
        'updated_at': current_time
    }

    print(new_message)
    message_created = await Message(**new_message).insert()
    await notify_new_message(message_created, str(recipient_user.id))
    return message_created

@router.get('', dependencies=[Depends(require_role("admin"))], response_model=List[MessageResponse])
async def get_all_messages_list_for_user(current_user: User = Depends(get_current_user)):
    """Get all messages received by the current user"""
    messages = await Message.find({
        "$or": [
            {
                "recipientUserId": current_user.id,
                "isDeletedForRecipient": False
            },
            {
                "senderUserId": current_user.id,
                "isDeletedForSender": False
            }
        ]
    }).to_list()

    messages = evaluate_message_read_status(messages, current_user)
    return messages

@router.get("/count", response_model=MessageCountResponse)
async def get_message_count(current_user: User = Depends(get_current_user)):
    """Get count of messages by the current user"""
    messages = await Message.find({
        "$or": [
            {
                "recipientUserId": current_user.id,
                "isDeletedForRecipient": False
            },
            {
                "senderUserId": current_user.id,
                "isDeletedForSender": False
            }
        ]
    }).to_list()

    messages = evaluate_message_read_status(messages, current_user)
    
    read_count = len([message for message in messages if message.isRead])
    unread_count = len([message for message in messages if not message.isRead])
    total_count = len(messages)
    
    return MessageCountResponse(
        read=read_count, 
        unread=unread_count, 
        total=total_count
    )

@router.put('/read', dependencies=[Depends(require_role("admin"))], response_model=dict)
async def mark_message_as_read(read_message_body: ReadMessageBody, current_user: User = Depends(get_current_user)):
    """Mark all messages in the list as read"""
    message_ids = [PydanticObjectId(message_id) for message_id in read_message_body.messageIds]

    await Message.find({
        "$and": [
            {"_id": {"$in": message_ids}},
            {"recipientUserId": current_user.id},
            {"isDeletedForRecipient": False}
        ]
    }).update({"$set": {"isRead": True, "updated_at": datetime.now(timezone.utc)}})

    updated_messages = await Message.find({"_id": {"$in": message_ids}}).to_list()
    message_ids_str = [str(msg.id) for msg in updated_messages]
    participant_ids = {str(current_user.id)}
    for message in updated_messages:
        if message.senderUserId:
            participant_ids.add(str(message.senderUserId))

    await notify_messages_read(message_ids_str, list(participant_ids))

    return {"message": "Messages marked as read successfully"}

@router.delete("/{message_id}", dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_message(message_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    """Delete a message"""
    message = await Message.find_one({
        "$and": [
            {"_id": message_id},
            {
                "$or": [
                    {"senderUserId": current_user.id},
                    {"recipientUserId": current_user.id}
                ]
            }
        ]
    })
    message_found = False

    # Message is sent by the current user
    if (message and message.senderUserId == current_user.id and not message.isDeletedForSender):
        message_found = True
        message.isDeletedForSender = True
    
    elif (message and message.recipientUserId == current_user.id and not message.isDeletedForRecipient):
        message_found = True
        message.isDeletedForRecipient = True

    if not message_found:
        raise HTTPException(
            status_code=400, 
            detail=Error(
                message="Message is not found", 
                status_code=400
            ).model_dump()
        )

    if message.isDeletedForSender and message.isDeletedForRecipient:
        await message.delete()
    else:
        await message.save()
    return {"message": "Message deleted successfully"}

@router.delete("/conversation/{conversation_id}", dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_conversation(conversation_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    """Delete all messages in a conversation"""
    # Find all messages in this conversation where the current user is a participant
    messages = await Message.find({
        "$and": [
            {"conversationId": conversation_id},
            {
                "$or": [
                    {"senderUserId": current_user.id},
                    {"recipientUserId": current_user.id}
                ]
            }
        ]
    }).to_list()
    
    if not messages:
        raise HTTPException(
            status_code=404,
            detail=Error(
                message="Conversation not found or you don't have access to it",
                status_code=404
            ).model_dump()
        )
    
    deleted_count = 0
    
    # Process each message in the conversation
    for message in messages:
        message_updated = False
        
        # If current user is the sender, mark as deleted for sender
        if message.senderUserId == current_user.id and not message.isDeletedForSender:
            message.isDeletedForSender = True
            message_updated = True
        
        # If current user is the recipient, mark as deleted for recipient
        if message.recipientUserId == current_user.id and not message.isDeletedForRecipient:
            message.isDeletedForRecipient = True
            message_updated = True
        
        # Only update/delete if message was actually modified
        if message_updated:
            # Count all messages deleted from user's end
            deleted_count += 1
            
            # If both parties have deleted it, permanently delete the message
            if message.isDeletedForSender and message.isDeletedForRecipient:
                await message.delete()
            else:
                # Otherwise, just update the flags (soft delete)
                await message.save()
    
    return {
        "message": f"Conversation deleted successfully",
        "deleted_count": deleted_count
    }