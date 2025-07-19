from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.certification import Certification as CertificationModel
from app.schemas.certification import Certification as CertificationSchema
from app.schemas.certification import CertificationCreate as CertificationCreateSchema
from typing import List

router = APIRouter()

@router.get('/certifications', response_model=List[CertificationSchema])
def read_certifications(db: Session = Depends(get_db)):
    certifications = db.query(CertificationModel).all()
    return certifications

@router.post('/certifications', response_model=CertificationSchema)
def create_certification(certification: CertificationCreateSchema, db: Session = Depends(get_db)):
    db_certification = CertificationModel(**certification.model_dump())
    db.add(db_certification)
    db.commit()
    db.refresh(db_certification)
    return db_certification

@router.get('/certifications/{certification_id}', response_model=CertificationSchema)
def get_certification(certification_id: int, db: Session = Depends(get_db)):
    db_certification = db.query(CertificationModel).filter(CertificationModel.id == certification_id).first()
    if db_certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    return db_certification

@router.put('/certifications/{certification_id}', response_model=CertificationSchema)
def update_certification(certification_id: int, certification: CertificationCreateSchema, db: Session = Depends(get_db)):
    db_certification = db.query(CertificationModel).filter(CertificationModel.id == certification_id).first()
    if db_certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    for key, value in certification.model_dump().items():
        setattr(db_certification, key, value)
    db.commit()
    db.refresh(db_certification)
    return db_certification

@router.delete('/certifications/{certification_id}', response_model=dict)
def delete_certification(certification_id: int, db: Session = Depends(get_db)):
    db_certification = db.query(CertificationModel).filter(CertificationModel.id == certification_id).first()
    if db_certification is None:
        raise HTTPException(status_code=404, detail='Certification not found')
    db.delete(db_certification)
    db.commit()
    return {'message': 'Certification deleted successfully'}