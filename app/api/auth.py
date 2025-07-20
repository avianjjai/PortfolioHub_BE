from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import require_role, pwd_context, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.enums.user import UserRole, UserStatus

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    new_user = User(
        email=user.email,
        username=user.email,
        hashed_password=pwd_context.hash(user.password),
        role=UserRole.admin,
        is_active=UserStatus.active
    )

    await new_user.insert()
    return UserResponse(**new_user.model_dump())

@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.username == form_data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(form_data.password, user.hashed_password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_active is UserStatus.inactive:
        raise HTTPException(status_code=401, detail="Inactive user")

    access_token = create_access_token(
        data={
            "username": user.username,
            "role": user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user.model_dump(exclude={"hashed_password"})