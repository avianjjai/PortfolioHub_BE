from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import asyncio
from app.utils.auth import require_role, pwd_context, create_access_token, get_current_user, verify_token, oauth2_scheme
from app.utils.token_cleanup import cleanup_expired_tokens, get_blacklist_stats
from app.models.user import User
from app.models.access_token import AccessToken
from app.schemas.user import UserCreate, UserResponse
from app.enums.user import UserRole, UserStatus
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    if await User.find_one(User.email == user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=pwd_context.hash(user.password),
        role=UserRole.viewer,  # Default role is viewer, not admin
        is_active=UserStatus.active,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        title=user.title
    )

    return await new_user.insert()

@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.username == form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(form_data.password, user.hashed_password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_active is UserStatus.inactive:
        raise HTTPException(status_code=401, detail="Inactive user")

    access_token = await create_access_token(
        data={
            "username": user.username,
            "role": user.role
        },
        user_id=user.id
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user.model_dump(exclude={"hashed_password"})

@router.post("/auth/refresh")
async def refresh_token(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Refresh the access token, extending the expiry time."""
    # Delete old token
    old_token = await AccessToken.find_one(AccessToken.token == token)
    if old_token:
        await old_token.delete()
    
    # Create new token
    new_access_token = await create_access_token(
        data={
            "username": current_user.username,
            "role": current_user.role
        },
        user_id=current_user.id
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Logout user by deleting the current token from database."""
    # Delete the token from database
    token_doc = await AccessToken.find_one(AccessToken.token == token)
    if token_doc:
        await token_doc.delete()
        return {"message": "Successfully logged out"}
    else:
        # Token already deleted or doesn't exist
        return {"message": "Token already revoked"}

@router.post("/auth/cleanup-tokens", dependencies=[Depends(require_role("admin"))])
async def manual_cleanup_tokens(current_user: User = Depends(get_current_user)):
    """Manually trigger cleanup of expired tokens (admin only)."""
    from app.utils.token_cleanup import cleanup_expired_access_tokens
    deleted_count = await cleanup_expired_access_tokens()
    stats = await get_token_stats()
    return {
        "message": "Cleanup completed",
        "deleted_tokens": deleted_count,
        "stats": stats
    }

@router.get("/auth/token-stats", dependencies=[Depends(require_role("admin"))])
async def get_token_stats(current_user: User = Depends(get_current_user)):
    """Get statistics about active tokens (admin only)."""
    current_time = datetime.now(timezone.utc)
    total_count = await AccessToken.count()
    expired_count = await AccessToken.find(
        AccessToken.expires_at < current_time
    ).count()
    
    return {
        "total_tokens": total_count,
        "expired_tokens": expired_count,
        "active_tokens": total_count - expired_count
    }