from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.schemas.user import UserResponse
from beanie import PydanticObjectId
from datetime import datetime

router = APIRouter()

# get user by id
@router.get('/user/{user_id}', response_model=UserResponse)
async def get_user_by_id(user_id: PydanticObjectId):
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user.model_dump(exclude={"hashed_password"})

# increment visitor count
@router.post('/user/{user_id}/increment-visitor')
async def increment_visitor_count(user_id: PydanticObjectId):
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Increment visitor count
    if user.visitor_count is None:
        user.visitor_count = 0
    user.visitor_count += 1
    user.updated_at = datetime.now()
    await user.save()
    
    return {"visitor_count": user.visitor_count}