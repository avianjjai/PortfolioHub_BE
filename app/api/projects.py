from fastapi import APIRouter
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import List
from fastapi import Depends, HTTPException
from app.utils.auth import require_role
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId
router = APIRouter()

# get projects by user id
@router.get('/projects/user/{user_id}', response_model=List[Project])
async def read_projects_by_user(user_id: str):
    projects = await Project.find(Project.user_id == ObjectId(user_id)).to_list()
    return projects

# get perticular project by id
@router.get('/projects/{project_id}', response_model=Project)
async def get_project_by_id(project_id: str):
    project = await Project.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    return project

# create project
@router.post('/projects', dependencies=[Depends(require_role("admin"))], response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    new_project = {**project.model_dump(), 'user_id': current_user.id}
    return await Project(**new_project).insert()

# update project
@router.put('/projects/{project_id}', dependencies=[Depends(require_role("admin"))], response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate, current_user: User = Depends(get_current_user)):
    updated_project = await Project.get(project_id)

    if updated_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    if updated_project.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to update this project')
    for key, value in project.model_dump().items():
        setattr(updated_project, key, value)

    updated_project.updated_at = datetime.now(timezone.utc) # type: ignore

    await updated_project.save()
    return updated_project

# delete project
@router.delete('/projects/{project_id}', dependencies=[Depends(require_role("admin"))], response_model=dict)
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    target_project = await Project.get(project_id)
    if target_project is None:
        raise HTTPException(status_code=404, detail='Project not found')
    if target_project.user_id != ObjectId(current_user.id):
        raise HTTPException(status_code=403, detail='You are not allowed to delete this project')
    await target_project.delete()
    return {'message': 'Project deleted successfully'}

