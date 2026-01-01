from fastapi import APIRouter, Depends, HTTPException
from app.models.education import Education
from app.schemas.education import EducationCreate
from typing import List
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId
from app.schemas.error import Error
from beanie import PydanticObjectId

router = APIRouter()

# get current user's educations
@router.get('', response_model=List[Education])
async def get_current_user_educations(current_user: User = Depends(get_current_user)):
    return await Education.find(Education.user_id == ObjectId(current_user.id)).to_list()

# get educations by user id
@router.get('/user/{user_id}', response_model=List[Education])
async def read_educations_by_user(user_id: PydanticObjectId):
    return await Education.find(Education.user_id == user_id).to_list()

# create education
@router.post('', response_model=Education)
async def create_education(education: EducationCreate, current_user: User = Depends(get_current_user)):
    new_education = {**education.model_dump(), 'user_id': current_user.id}
    education_created = await Education(**new_education).insert()
    return education_created

# update education
@router.put('/{education_id}', response_model=Education)
async def update_education(education_id: str, education: EducationCreate, current_user: User = Depends(get_current_user)):
    updated_education = await Education.get(education_id)
    if updated_education is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Education not found', 
                status_code=404
            ).model_dump()
        )
    if updated_education.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to update this education', 
                status_code=403
            ).model_dump()
        )
    for key, value in education.model_dump().items():
        setattr(updated_education, key, value)
    updated_education.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_education.save()
    return updated_education

# delete education
@router.delete('/{education_id}', response_model=dict)
async def delete_education(education_id: str, current_user: User = Depends(get_current_user)):
    target_education = await Education.get(education_id)
    if target_education is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Education not found', 
                status_code=404
            ).model_dump()
        )
    if target_education.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to delete this education', 
                status_code=403
            ).model_dump()
        )
    await target_education.delete()
    return {'message': 'Education deleted successfully'}