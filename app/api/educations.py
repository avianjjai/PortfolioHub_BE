from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.education import Education as EducationModel
from app.schemas.education import Education as EducationSchema
from app.schemas.education import EducationCreate as EducationCreateSchema
from typing import List

router = APIRouter()

@router.get('/educations', response_model=List[EducationSchema])
def read_educations(db: Session = Depends(get_db)):
    educations = db.query(EducationModel).all()
    return educations

@router.post('/educations', response_model=EducationSchema)
def create_education(education: EducationCreateSchema, db: Session = Depends(get_db)):
    db_education = EducationModel(**education.model_dump())
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return db_education

@router.get('/educations/{education_id}', response_model=EducationSchema)
def get_education(education_id: int, db: Session = Depends(get_db)):
    db_education = db.query(EducationModel).filter(EducationModel.id == education_id).first()
    if db_education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    return db_education

@router.put('/educations/{education_id}', response_model=EducationSchema)
def update_education(education_id: int, education: EducationCreateSchema, db: Session = Depends(get_db)):
    db_education = db.query(EducationModel).filter(EducationModel.id == education_id).first()
    if db_education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    for key, value in education.model_dump().items():
        setattr(db_education, key, value)
    db.commit()
    db.refresh(db_education)
    return db_education

@router.delete('/educations/{education_id}', response_model=dict)
def delete_education(education_id: int, db: Session = Depends(get_db)):
    db_education = db.query(EducationModel).filter(EducationModel.id == education_id).first()
    if db_education is None:
        raise HTTPException(status_code=404, detail='Education not found')
    db.delete(db_education)
    db.commit()
    return {'message': 'Education deleted successfully'}