from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base

class Education(Base):
    __tablename__ = 'educations'
    id = Column(Integer, primary_key=True, index=True)
    institution = Column(String, index=True)
    degree = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(String)