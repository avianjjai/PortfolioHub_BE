from fastapi import APIRouter, Depends, HTTPException
from app.models.education import Education
from app.schemas.education import EducationCreate
from typing import List
from app.utils.auth import require_role
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId
router = APIRouter()

# get educations by user id
@router.get('/educations/user/{user_id}', response_model=List[Education])
async def read_educations_by_user(user_id: str):
    return await Education.find(Education.user_id == ObjectId(user_id)).to_list()

# get perticular education by id
@router.get('/educations/{education_id}', response_model=Education)
async def get_education_by_id(education_id: str):
    education = await Education.get(education_id)
    if education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    return education

# create education
@router.post('/educations', dependencies=[Depends(require_role("admin"))], response_model=Education)
async def create_education(education: EducationCreate, current_user: User = Depends(get_current_user)):
    new_education = {**education.model_dump(), 'user_id': current_user.id}
    education_created = await Education(**new_education).insert()
    return education_created

# update education
@router.put('/educations/{education_id}', dependencies=[Depends(require_role("admin"))], response_model=Education)
async def update_education(education_id: str, education: EducationCreate, current_user: User = Depends(get_current_user)):
    updated_education = await Education.get(education_id)
    if updated_education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    if updated_education.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to update this education')
    for key, value in education.model_dump().items():
        setattr(updated_education, key, value)
    updated_education.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_education.save()
    return updated_education

# delete education
@router.delete('/educations/{education_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_education(education_id: str, current_user: User = Depends(get_current_user)):
    target_education = await Education.get(education_id)
    if target_education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    if target_education.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to delete this education')
    await target_education.delete()
    return {'message': 'Education deleted successfully'}