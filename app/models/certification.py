from beanie import Document
from datetime import datetime
from app.models.user import User

class Certification(Document):
    user: User
    name: str
    issuing_organization: str
    issue_date: datetime
    expiration_date: datetime
    credential_id: str
    credential_url: str

    class Settings:
        name = "certifications"
        indexes = [
            "name",
        ]