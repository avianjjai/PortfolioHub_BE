from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.models.access_token import AccessToken
from app.config import settings
from beanie import PydanticObjectId
from bson import ObjectId
import re
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") 

# Secret key for JWT - from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", settings.secret_key)
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Validate that SECRET_KEY is set and not default
if SECRET_KEY == "your-secret-key-here" or SECRET_KEY == "your-256-bit-secret-key":
    import warnings
    warnings.warn(
        "WARNING: Using default SECRET_KEY! This is insecure. "
        "Please set SECRET_KEY environment variable for production.",
        UserWarning
    )

# Password hashing
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

async def create_access_token(data: dict, user_id: PydanticObjectId, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """Create a JWT access token and store it in the database."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store token in database
    token_doc = AccessToken(
        token=token,
        user_id=user_id,
        username=data.get("username", ""),
        role=str(data.get("role", "")),
        expires_at=expire
    )
    await token_doc.insert()
    
    return token

async def is_token_valid(token: str) -> bool:
    """Check if a token exists in the database (not deleted)."""
    token_doc = await AccessToken.find_one(AccessToken.token == token)
    if token_doc is None:
        return False
    
    # Check if token has expired
    current_time = datetime.now(timezone.utc)
    # Ensure expires_at is timezone-aware for comparison
    expires_at = token_doc.expires_at
    if expires_at.tzinfo is None:
        # If timezone-naive, assume it's UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < current_time:
        # Auto-delete expired token
        await token_doc.delete()
        return False
    
    return True

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
    # First verify JWT signature
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if token exists in database (not deleted)
    if not await is_token_valid(token):
        raise HTTPException(status_code=401, detail="Token has been revoked or expired")
    
    # Update last_used_at timestamp
    token_doc = await AccessToken.find_one(AccessToken.token == token)
    if token_doc:
        token_doc.last_used_at = datetime.now(timezone.utc)
        await token_doc.save()
    
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

async def get_current_user_with_refresh(token: str = Depends(oauth2_scheme)):
    """
    Get current user and optionally refresh token.
    Returns tuple of (user, new_token) where new_token is None if refresh is not needed.
    """
    user = await get_current_user(token)
    
    # Check if token is close to expiring (within 5 minutes)
    payload = verify_token(token)
    if payload:
        exp = payload.get("exp")
        if exp:
            exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            time_until_expiry = exp_time - datetime.now(timezone.utc)
            # If token expires in less than 5 minutes, refresh it
            if time_until_expiry.total_seconds() < 300:  # 5 minutes
                new_token = await create_access_token(
                    data={
                        "username": user.username,
                        "role": user.role
                    },
                    user_id=user.id
                )
                return user, new_token
    
    return user, None