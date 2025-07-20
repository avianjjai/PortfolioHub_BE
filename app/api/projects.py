from fastapi import APIRouter
from app.models.project import Project as ProjectModel
from app.schemas.project import Project as ProjectSchema
from app.schemas.project import ProjectCreate as ProjectCreateSchema, ProjectUpdate as ProjectUpdateSchema
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.database import get_db
from app.utils.auth import require_role
from datetime import datetime, timezone

router = APIRouter()

# Defines the route for reading all projects
# Uses dependency injection to get the database session
# Returns ORM objects
@router.get('/projects', response_model=List[ProjectSchema])
def read_projects(db: Session = Depends(get_db)):
    return db.query(ProjectModel).all()

# Defines the route for creating a new project
@router.post('/projects', dependencies=[Depends(require_role("admin"))], response_model=ProjectSchema)
def create_project(project: ProjectCreateSchema, db: Session = Depends(get_db)):
    db_project = ProjectModel(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put('/projects/{project_id}', dependencies=[Depends(require_role("admin"))], response_model=ProjectSchema)
def update_project(project_id: int, project: ProjectUpdateSchema, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    for key, value in project.model_dump().items():
        setattr(db_project, key, value)

    db_project.updated_at = datetime.now(timezone.utc) # type: ignore

    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete('/projects/{project_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    db.delete(db_project)
    db.commit()
    return {'message': 'Project deleted successfully'}

@router.get('/projects/{project_id}', response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    return db_project