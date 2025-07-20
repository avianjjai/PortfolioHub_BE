from pydantic import BaseModel
from beanie import PydanticObjectId
from datetime import datetime

class AboutBase(BaseModel):
    title: str
    first_name: str
    middle_name: str
    last_name: str
    email: str
    phone: str
    address: str
    profile_image_url: str

class AboutCreate(AboutBase):
    pass

class About(AboutBase):
    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
