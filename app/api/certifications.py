from fastapi import APIRouter, Depends, HTTPException
from app.models.certification import Certification
from app.schemas.certification import CertificationCreate
from typing import List
from app.utils.auth import require_role
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId

router = APIRouter()

# get certifications by user id
@router.get('/certifications/user/{user_id}', response_model=List[Certification])
async def read_certifications_by_user(user_id: str):
    return await Certification.find(Certification.user_id == ObjectId(user_id)).to_list()

# get perticular certification by id
@router.get('/certifications/{certification_id}', response_model=Certification)
async def get_certification_by_id(certification_id: str):
    certification = await Certification.get(certification_id)
    if certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    return certification

# create certification
@router.post('/certifications', dependencies=[Depends(require_role("admin"))], response_model=Certification)
async def create_certification(certification: CertificationCreate, current_user: User = Depends(get_current_user)):
    new_certification = {**certification.model_dump(), 'user_id': current_user.id}
    certification_created = await Certification(**new_certification).insert()
    return certification_created

# update certification
@router.put('/certifications/{certification_id}', dependencies=[Depends(require_role("admin"))], response_model=Certification)
async def update_certification(certification_id: str, certification: CertificationCreate, current_user: User = Depends(get_current_user)):
    updated_certification = await Certification.get(certification_id)
    if updated_certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    if updated_certification.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to update this certification')
    for key, value in certification.model_dump().items():
        setattr(updated_certification, key, value)
    updated_certification.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_certification.save()
    return updated_certification
    
# delete certification
@router.delete('/certifications/{certification_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_certification(certification_id: str, current_user: User = Depends(get_current_user)):
    target_certification = await Certification.get(certification_id)
    if target_certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    if target_certification.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to delete this certification')
    await target_certification.delete()
    return {'message': 'Certification deleted successfully'}