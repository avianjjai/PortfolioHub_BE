from unicodedata import category
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SkillBase(BaseModel):
    name: str
    category: str
    proficiency: int = Field(ge=0, le=100)

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None
    category: Optional[str] = None
    proficiency: Optional[int] = Field(ge=0, le=100)

class Skill(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True