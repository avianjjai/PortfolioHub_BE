from pydantic import BaseModel

# ProjectBase is the base schema for the shared fields
class ProjectBase(BaseModel):
    title: str
    description: str
    link: str
    image_url: str

# ProjectCreate is the schema for creating new projects (no id)
class ProjectCreate(ProjectBase):
    pass

# Pydantic model for reading projects (includes id)
class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True