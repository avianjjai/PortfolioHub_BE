from beanie import Document, PydanticObjectId
from app.enums.user import UserRole, UserStatus
from datetime import datetime
from typing import Optional, List
from app.enums.user import UserGender

class User(Document):
    # Authentication & Basic Info
    username: str
    email: str
    hashed_password: str
    is_active: UserStatus = UserStatus.active
    role: UserRole = UserRole.admin
    
    # Personal Information
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    gender: Optional[UserGender] = None
    
    # Contact Information
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image_url: Optional[str] = None
    
    # Portfolio/About Information (merged from About collection)
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
    
    # Analytics
    visitor_count: int = 0
    
    # System Fields
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "users"
        indexes = [
            "username",
            "email",
        ]