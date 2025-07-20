from pydantic import BaseModel
from datetime import date, datetime
from beanie import PydanticObjectId
from typing import Optional

class CertificationBase(BaseModel):
    name: str
    issuer: str
    issue_date: date
    description: str
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

class CertificationCreate(CertificationBase):
    pass

class Certification(CertificationBase):
    id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime