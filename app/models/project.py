from app.db.database import Base
from sqlalchemy import Column, DateTime, Integer, String, JSON
from datetime import datetime, timezone

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    technologies = Column(JSON)
    live_url = Column(String)
    code_url = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))