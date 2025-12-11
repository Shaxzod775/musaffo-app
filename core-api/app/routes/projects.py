from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from app.models.models import Project
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/projects", tags=["projects"])
db = get_db()

@router.get("", response_model=List[dict])
async def get_all_projects():
    """Get all projects"""
    try:
        projects_ref = db.collection('projects')
        docs = projects_ref.stream()
        projects_list = []
        for doc in docs:
            project_data = doc.to_dict()
            project_data['id'] = doc.id
            projects_list.append(project_data)
        return projects_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project_by_id(project_id: str):
    """Get project by ID"""
    try:
        doc = db.collection('projects').document(project_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        project_data = doc.to_dict()
        project_data['id'] = doc.id
        return project_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", status_code=201)
async def create_project(project: Project):
    """Create new project"""
    try:
        project_dict = project.model_dump(exclude={'id'})
        project_dict['createdAt'] = datetime.now()
        project_dict['updatedAt'] = datetime.now()
        
        doc_ref = db.collection('projects').document()
        doc_ref.set(project_dict)
        
        return {"id": doc_ref.id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}")
async def update_project(project_id: str, updates: dict):
    """Update project (e.g., currentAmount)"""
    try:
        project_ref = db.collection('projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        updates['updatedAt'] = datetime.now()
        project_ref.update(updates)
        
        return {"message": "Project updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
