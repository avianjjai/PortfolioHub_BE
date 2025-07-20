from beanie import Document
from datetime import datetime
from typing import Optional
from app.models.user import User

class Education(Document):
    user: User
    institution: str
    degree: str
    start_date: datetime
    end_date:    datetime
    description: str

    class Settings:
        name = "educations"
        indexes = [
            "institution",
        ]