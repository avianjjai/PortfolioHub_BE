from sqlalchemy import Column, Integer, String
from app.db.database import Base

class About(Base):
    __tablename__ = 'about'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    first_name = Column(String, index=True)
    middle_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    profile_image_url = Column(String)