from fastapi import APIRouter, Depends, HTTPException
from app.models.about import About
from app.schemas.about import AboutCreate
from app.utils.auth import require_role
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()

# get about by user id
@router.get('/about/user/{user_id}', response_model=About)
async def read_about_by_user(user_id: str):
    return await About.find(About.user.id == user_id).to_list()

# create about
@router.post('/about', dependencies=[Depends(require_role("admin"))], response_model=About)
async def create_about(about: AboutCreate, current_user: User = Depends(get_current_user)):
    new_about = {**about.model_dump(), 'user': current_user}
    await About(**new_about).insert()
    return new_about

# get about by id
@router.get('/about/{about_id}', response_model=About)
async def get_about_by_id(about_id: str):
    about = await About.get(about_id)
    if about is None:
        raise HTTPException(status_code=404, detail='About not found')
    return about

# update about
@router.put('/about/{about_id}', dependencies=[Depends(require_role("admin"))], response_model=About)
async def update_about(about_id: str, about: AboutCreate, current_user: User = Depends(get_current_user)):
    updated_about = await About.get(about_id)
    if updated_about is None:
        raise HTTPException(status_code=404, detail='About not found')
    if updated_about.user.id != current_user.id:
        raise HTTPException(status_code=403, detail='You are not allowed to update this about')
    for key, value in about.model_dump().items():
        setattr(updated_about, key, value)
    updated_about.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_about.save()
    return updated_about

# delete about
@router.delete('/about/{about_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_about(about_id: str, current_user: User = Depends(get_current_user)):
    target_about = await About.get(about_id)
    if target_about is None:
        raise HTTPException(status_code=404, detail='About not found')
    if target_about.user.id != current_user.id:
        raise HTTPException(status_code=403, detail='You are not allowed to delete this about')
    await target_about.delete()
    return {'message': 'About deleted successfully'}