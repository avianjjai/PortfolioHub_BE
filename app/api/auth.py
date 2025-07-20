from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.auth import require_role, pwd_context, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.enums.user import UserRole, UserStatus

router = APIRouter()

@router.post("/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_active is False:
        raise HTTPException(status_code=401, detail="Inactive user")

    access_token = create_access_token(
        data={
            "username": user.username,
            "role": user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        email=user.email,
        username=user.email,
        hashed_password=pwd_context.hash(user.password),
        role=UserRole.admin,
        is_active=UserStatus.active
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(
        data={
            "username": db_user.email,
            "role": db_user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    # remove password from response
    return current_user