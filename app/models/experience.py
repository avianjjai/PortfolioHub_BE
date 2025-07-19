from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base

class Experience(Base):
    __tablename__ = 'experiences'
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    position = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    description = Column(String)