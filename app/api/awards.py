from fastapi import APIRouter, Depends, HTTPException
from app.models.award import Award
from app.schemas.award import AwardCreate
from typing import List
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId
from app.schemas.error import Error
from beanie import PydanticObjectId

router = APIRouter()

# get awards by user id
@router.get('/awards/user/{user_id}', response_model=List[Award])
async def read_awards_by_user(user_id: PydanticObjectId):
    return await Award.find(Award.user_id == user_id).to_list()

# create award
@router.post('/awards', response_model=Award)
async def create_award(award: AwardCreate, current_user: User = Depends(get_current_user)):
    new_award = {**award.model_dump(), 'user_id': current_user.id}
    award_created = await Award(**new_award).insert()
    return award_created

# update award
@router.put('/awards/{award_id}', response_model=Award)
async def update_award(award_id: str, award: AwardCreate, current_user: User = Depends(get_current_user)):
    updated_award = await Award.get(award_id)
    if updated_award is None:
        raise HTTPException(
            status_code=404, detail=Error(
                message='Award not found', 
                status_code=404
            ).model_dump()
        )
    if updated_award.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to update this award', 
                status_code=403
            ).model_dump()
        )
    for key, value in award.model_dump().items():
        setattr(updated_award, key, value)
    updated_award.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_award.save()
    return updated_award
    
# delete award
@router.delete('/awards/{award_id}', response_model=dict)
async def delete_award(award_id: str, current_user: User = Depends(get_current_user)):
    target_award = await Award.get(award_id)
    if target_award is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Award not found', 
                status_code=404
            ).model_dump()
        )
    if target_award.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to delete this award', 
                status_code=403
            ).model_dump()
        )
    await target_award.delete()
    return {'message': 'Award deleted successfully'}
