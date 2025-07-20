from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") 

# Secret key for JWT
SECRET_KEY = "your-256-bit-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict | None:
    """Verify a JWT token and return the payload, or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Update this function to use Beanie instead of SQLAlchemy
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract the username from a valid JWT token, or raise HTTPException if invalid."""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    username = payload.get("username")
    user = await User.find_one(User.username == username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_active is False:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:  # type: ignore
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency



