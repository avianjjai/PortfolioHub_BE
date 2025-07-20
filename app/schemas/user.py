from pydantic import BaseModel
from app.enums.user import UserRole, UserStatus
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: Optional[UserRole] = UserRole.viewer
    is_active: Optional[UserStatus] = UserStatus.active

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True