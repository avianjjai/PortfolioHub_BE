from pydantic import BaseModel
from enum import Enum
from app.enums.user import UserRole, UserStatus

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: UserRole
    is_active: UserStatus
    username: str

    class Config:
        from_attributes = True