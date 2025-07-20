from beanie import Document, PydanticObjectId
from datetime import datetime, timezone

class Certification(Document):
    user_id: PydanticObjectId
    name: str
    issuer: str
    issue_date: datetime
    description: str
    credential_id: str
    credential_url: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "certifications"
        indexes = [
            "name",
        ]