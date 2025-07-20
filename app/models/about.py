from beanie import Document
from app.models.user import User

class About(Document):
    user: User
    title: str
    first_name: str
    middle_name: str
    last_name: str
    email: str
    phone: str
    address: str
    profile_image_url: str

    class Settings:
        name = "about"
        indexes = [
            "title",
        ]