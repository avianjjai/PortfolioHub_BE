from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExperienceBase(BaseModel):
    title: str
    description: str
    technologies: List[str]
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Experience(ExperienceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True