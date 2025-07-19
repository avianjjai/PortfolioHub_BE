from pydantic import BaseModel
from datetime import date

class ExperienceBase(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: date
    description: str

class ExperienceCreate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: int

    class Config:
        from_attributes = True