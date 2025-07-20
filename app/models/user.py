from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base
from app.enums.user import UserRole, UserStatus

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(String, default=UserStatus.active)
    role = Column(String, default=UserRole.admin)