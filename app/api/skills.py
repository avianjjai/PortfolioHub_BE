from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate
from app.utils.auth import get_current_user
from datetime import datetime, timezone
from app.models.user import User
from bson import ObjectId
from app.schemas.error import Error
from beanie import PydanticObjectId

router = APIRouter()

# get skills by user id
@router.get('/skills/user/{user_id}', response_model=List[Skill])
async def read_skills_by_user(user_id: PydanticObjectId):
    return await Skill.find(Skill.user_id == user_id).to_list()

# create skill
@router.post('/skills', response_model=Skill)
async def create_skill(skill: SkillCreate, current_user: User = Depends(get_current_user)):
    # check if skill already exists
    existing_skill = await Skill.find_one(Skill.name == skill.name, Skill.user_id == ObjectId(current_user.id))
    if existing_skill:
        raise HTTPException(
            status_code=400, 
            detail=Error(
                message='Skill already exists', 
                status_code=400
            ).model_dump()
        )

    new_skill = {**skill.model_dump(), 'user_id': current_user.id}
    skill_created = await Skill(**new_skill).insert()
    return skill_created


# update skill
@router.put('/skills/{skill_id}', response_model=Skill)
async def update_skill(skill_id: str, skill: SkillUpdate, current_user: User = Depends(get_current_user)):
    updated_skill = await Skill.get(skill_id)
    if updated_skill is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Skill not found', 
                status_code=404
            ).model_dump()
        )
    if updated_skill.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to update this skill', 
                status_code=403
            ).model_dump()
        )
    for key, value in skill.model_dump().items():
        setattr(updated_skill, key, value)
    updated_skill.updated_at = datetime.now(timezone.utc) # type: ignore
    await updated_skill.save()
    return updated_skill

# delete skill
@router.delete('/skills/{skill_id}', response_model=dict)
async def delete_skill(skill_id: str, current_user: User = Depends(get_current_user)):
    target_skill = await Skill.get(skill_id)
    if target_skill is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Skill not found', 
                status_code=404
            ).model_dump()
        )
    if target_skill.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to delete this skill', 
                status_code=403
            ).model_dump()
        )
    await target_skill.delete()
    return {'message': 'Skill deleted successfully'}