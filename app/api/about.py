from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.about import About as AboutModel
from app.schemas.about import About as AboutSchema
from app.schemas.about import AboutCreate as AboutCreateSchema

router = APIRouter()

@router.get('/about', response_model=AboutSchema)
def read_about(db: Session = Depends(get_db)):
    about = db.query(AboutModel).first()
    if not about:
        raise HTTPException(status_code=404, detail='About not found')
    return about

@router.post('/about', response_model=AboutSchema)
def create_about(about: AboutCreateSchema, db: Session = Depends(get_db)):
    db_about = AboutModel(**about.model_dump())
    db.add(db_about)
    db.commit()
    db.refresh(db_about)
    return db_about

@router.get('/about/{about_id}', response_model=AboutSchema)
def get_about(about_id: int, db: Session = Depends(get_db)):
    db_about = db.query(AboutModel).filter(AboutModel.id == about_id).first()
    if not db_about:
        raise HTTPException(status_code=404, detail='About not found')
    return db_about

@router.put('/about/{about_id}', response_model=AboutSchema)
def update_about(about_id: int, about: AboutCreateSchema, db: Session = Depends(get_db)):
    db_about = db.query(AboutModel).filter(AboutModel.id == about_id).first()
    if not db_about:
        raise HTTPException(status_code=404, detail='About not found')
    for key, value in about.model_dump().items():
        setattr(db_about, key, value)
    db.commit()
    db.refresh(db_about)
    return db_about

@router.delete('/about/{about_id}', response_model=dict)
def delete_about(about_id: int, db: Session = Depends(get_db)):
    db_about = db.query(AboutModel).filter(AboutModel.id == about_id).first()
    if not db_about:
        raise HTTPException(status_code=404, detail='About not found')
    db.delete(db_about)
    db.commit()
    return {'message': 'About deleted successfully'}