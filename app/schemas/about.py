from pydantic import BaseModel

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
    id: int

    class Config:
        from_attributes = True
