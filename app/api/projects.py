from fastapi import APIRouter
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import List
from fastapi import Depends, HTTPException
from datetime import datetime, timezone
from app.utils.auth import get_current_user
from app.models.user import User
from bson import ObjectId
from app.schemas.error import Error
from beanie import PydanticObjectId
router = APIRouter()

# get projects by user id
@router.get('/projects/user/{user_id}', response_model=List[Project])
async def read_projects_by_user(user_id: PydanticObjectId):
    projects = await Project.find(Project.user_id == user_id).to_list()
    # sort by end_date if available, else start_date (matching experience section)
    projects.sort(key=lambda x: x.end_date if x.end_date else x.start_date, reverse=True)
    return projects

# create project
@router.post('/projects', response_model=Project)
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    print(project)
    new_project = {**project.model_dump(), 'user_id': current_user.id}
    return await Project(**new_project).insert()

# update project
@router.put('/projects/{project_id}', response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate, current_user: User = Depends(get_current_user)):
    updated_project = await Project.get(project_id)

    if updated_project is None:
        raise HTTPException(status_code=404, detail=Error(
            message='Project not found', 
            status_code=404
        ).model_dump())
    if updated_project.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to update this project', 
                status_code=403
            ).model_dump()
        )
    for key, value in project.model_dump().items():
        setattr(updated_project, key, value)

    updated_project.updated_at = datetime.now(timezone.utc) # type: ignore

    await updated_project.save()
    return updated_project

# delete project
@router.delete('/projects/{project_id}', response_model=dict)
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    target_project = await Project.get(project_id)
    if target_project is None:
        raise HTTPException(
            status_code=404, 
            detail=Error(
                message='Project not found', 
                status_code=404
            ).model_dump()
        )
    if target_project.user_id != ObjectId(current_user.id):
        raise HTTPException(
            status_code=403, 
            detail=Error(
                message='You are not allowed to delete this project', 
                status_code=403
            ).model_dump()
        )
    await target_project.delete()
    return {'message': 'Project deleted successfully'}

