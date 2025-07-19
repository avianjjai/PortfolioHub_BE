from sqlalchemy import Column, Integer, String
from app.db.database import Base

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    level = Column(String) # Beginner, Intermediate, Advanced, Expert