from pydantic import BaseModel

class SkillBase(BaseModel):
    name: str
    level: str

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int

    class Config:
        from_attributes = True