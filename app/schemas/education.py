from pydantic import BaseModel
from datetime import date, datetime
from beanie import PydanticObjectId
from typing import Optional

class EducationBase(BaseModel):
    institution: str
    degree: str
    start_date: date
    end_date: Optional[date] = None
    description: str
    
class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime 
    updated_at: datetime

    class Config:
        from_attributes = True