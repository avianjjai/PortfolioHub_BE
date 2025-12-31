from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date
from beanie import PydanticObjectId

# ProjectBase is the base schema for the shared fields
class ProjectBase(BaseModel):
    title: str
    description: str
    technologies: list[str]
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None

# ProjectCreate is the schema for creating new projects (no id)
class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[list[str]] = None
    live_url: Optional[str] = None
    code_url: Optional[str] = None
    image_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None