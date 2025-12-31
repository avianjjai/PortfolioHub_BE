from pydantic import BaseModel
from app.enums.user import UserRole, UserStatus
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: Optional[UserRole] = UserRole.viewer
    is_active: Optional[UserStatus] = UserStatus.active

class UserCreate(UserBase):
    username: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str
    title: Optional[str] = None
    phone: Optional[str] = None
    # Portfolio fields are optional during creation
    portfolio_title: Optional[str] = None
    portfolio_description: Optional[str] = None
    portfolio_education: Optional[List[str]] = None
    portfolio_certifications: Optional[List[str]] = None
    portfolio_awards: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: PydanticObjectId
    username: str
    email: str
    role: UserRole
    is_active: UserStatus
    title: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    # Portfolio fields
    portfolio_title: Optional[str] = None
    portfolio_description: Optional[str] = None
    portfolio_education: Optional[List[str]] = None
    portfolio_certifications: Optional[List[str]] = None
    portfolio_awards: Optional[List[str]] = None
    
    # Social Media Links
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    website_url: Optional[str] = None
    visitor_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PortfolioUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    portfolio_title: Optional[str] = None
    portfolio_description: Optional[str] = None
    portfolio_education: Optional[List[str]] = None
    portfolio_certifications: Optional[List[str]] = None
    portfolio_awards: Optional[List[str]] = None
    phone: Optional[str] = None
    
    # Social Media Links
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    website_url: Optional[str] = None