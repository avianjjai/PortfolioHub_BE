from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.experience import Experience
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.utils.auth import get_current_user
from app.models.user import User
from datetime import datetime, timezone
from bson import ObjectId
from app.schemas.error import Error
from beanie import PydanticObjectId

router = APIRouter()

# get experiences by user id
@router.get('/experiences/user/{user_id}', response_model=List[Experience])
async def read_experiences_by_user(user_id: PydanticObjectId):
    experiences = await Experience.find(Experience.user_id == user_id).to_list()
    experiences.sort(key=lambda x: x.end_date if x.end_date else x.start_date, reverse=True)
    return experiences

# create experience
@router.post('/experiences', response_model=Experience)
async def create_experience(experience: ExperienceCreate, current_user: User = Depends(get_current_user)):
    new_experience = {**experience.model_dump(), 'user_id': current_user.id}
    experience_created = await Experience(**new_experience).insert()
    return experience_created

# update experience
@router.put('/experiences/{experience_id}', response_model=Experience)
async def update_experience(experience_id: str, experience: ExperienceUpdate, current_user: User = Depends(get_current_user)):
    updated_experience = await Experience.get(experience_id)
    if updated_experience is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Experience not found', 
                status_code=404
            ).model_dump()
        )
    if updated_experience.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to update this experience', 
                status_code=403
            ).model_dump()
        )
    update_data = experience.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(updated_experience, key, value)
    updated_experience.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_experience.save()
    return updated_experience

# delete experience
@router.delete('/experiences/{experience_id}', response_model=dict)
async def delete_experience(experience_id: str, current_user: User = Depends(get_current_user)):
    target_experience = await Experience.get(experience_id)
    if target_experience is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Experience not found', 
                status_code=404
            ).model_dump()
        )
    if target_experience.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to delete this experience', 
                status_code=403
            ).model_dump()
        )
    await target_experience.delete()
    return {'message': 'Experience deleted successfully'}