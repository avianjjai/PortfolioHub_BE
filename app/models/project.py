from app.db.database import Base
from sqlalchemy import Column, Integer, String

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    link = Column(String)
    image_url = Column(String)