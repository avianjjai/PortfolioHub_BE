from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.experience import Experience as ExperienceModel
from app.schemas.experience import Experience as ExperienceSchema
from app.schemas.experience import ExperienceCreate as ExperienceCreateSchema
from app.utils.auth import require_role

router = APIRouter()

@router.get('/experiences', response_model=List[ExperienceSchema])
def read_experiences(db: Session = Depends(get_db)):
    experiences = db.query(ExperienceModel).all()
    return experiences

@router.post('/experiences', dependencies=[Depends(require_role("admin"))], response_model=ExperienceSchema)
def create_experience(experience: ExperienceCreateSchema, db: Session = Depends(get_db)):
    db_experience = ExperienceModel(**experience.model_dump())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

@router.get('/experiences/{experience_id}', response_model=ExperienceSchema)
def get_experience(experience_id: int, db: Session = Depends(get_db)):
    db_experience = db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
    if db_experience is None:
        raise HTTPException(status_code=404, detail='Experience not found')
    return db_experience

@router.put('/experiences/{experience_id}', dependencies=[Depends(require_role("admin"))], response_model=ExperienceSchema)
def update_experience(experience_id: int, experience: ExperienceCreateSchema, db: Session = Depends(get_db)):
    db_experience = db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
    if db_experience is None:
        raise HTTPException(status_code=404, detail='Experience not found')
    for key, value in experience.model_dump().items():
        setattr(db_experience, key, value)
    db.commit()
    db.refresh(db_experience)
    return db_experience

@router.delete('/experiences/{experience_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
def delete_experience(experience_id: int, db: Session = Depends(get_db)):
    db_experience = db.query(ExperienceModel).filter(ExperienceModel.id == experience_id).first()
    if db_experience is None:
        raise HTTPException(status_code=404, detail='Experience not found')
    db.delete(db_experience)
    db.commit()
    return {'message': 'Experience deleted successfully'}