from typing import List
from fastapi import APIRouter
from app.schemas.skill import Skill as SkillSchema
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.database import get_db
from app.models.skill import Skill as SkillModel
from app.schemas.skill import SkillCreate as SkillCreateSchema, SkillUpdate as SkillUpdateSchema
from app.utils.auth import require_role
from datetime import datetime, timezone

router = APIRouter()

@router.get('/skills', response_model=List[SkillSchema])
def read_skills(db: Session = Depends(get_db)):
    skills = db.query(SkillModel).all()
    return skills

@router.get('/skills/category/{category}', response_model=List[SkillSchema])
def read_skills_by_category(category: str, db: Session = Depends(get_db)):
    skills = db.query(SkillModel).filter(SkillModel.category == category).all()
    return skills


@router.post('/skills', dependencies=[Depends(require_role("admin"))], response_model=SkillSchema)
def create_skill(skill: SkillCreateSchema, db: Session = Depends(get_db)):
    # check if skill already exists
    existing_skill = db.query(SkillModel).filter(SkillModel.name == skill.name).first()
    if existing_skill:
        raise HTTPException(status_code=400, detail='Skill already exists')

    db_skill = SkillModel(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@router.get('/skills/{skill_id}', response_model=SkillSchema)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    db_skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail='Skill not found')
    return db_skill

@router.put('/skills/{skill_id}', dependencies=[Depends(require_role("admin"))], response_model=SkillSchema)
def update_skill(skill_id: int, skill: SkillUpdateSchema, db: Session = Depends(get_db)):
    db_skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail='Skill not found')
    for key, value in skill.model_dump().items():
        setattr(db_skill, key, value)

    db_skill.updated_at = datetime.now(timezone.utc) # type: ignore
    db.commit()
    db.refresh(db_skill)
    return db_skill

@router.delete('/skills/{skill_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    db_skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
    if db_skill is None:
        raise HTTPException(status_code=404, detail='Skill not found')
    db.delete(db_skill)
    db.commit()
    return {'message': 'Skill deleted successfully'}