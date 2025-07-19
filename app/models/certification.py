from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base

class Certification(Base):
    __tablename__ = 'certifications'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    issuing_organization = Column(String)
    issue_date = Column(Date)
    expiration_date = Column(Date)
    credential_id = Column(String)
    credential_url = Column(String)