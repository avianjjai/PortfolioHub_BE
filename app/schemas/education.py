from pydantic import BaseModel
from datetime import date

class EducationBase(BaseModel):
    institution: str
    degree: str
    start_date: date
    end_date: date
    description: str
    
class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: int

    class Config:
        from_attributes = True