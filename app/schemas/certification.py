from pydantic import BaseModel
from datetime import date

class CertificationBase(BaseModel):
    name: str
    issuing_organization: str
    issue_date: date
    expiration_date: date
    credential_id: str
    credential_url: str

class CertificationCreate(CertificationBase):
    pass

class Certification(CertificationBase):
    id: int

    class Config:
        from_attributes = True