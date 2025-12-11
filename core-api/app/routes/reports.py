from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from app.models.models import Report
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/reports", tags=["reports"])
db = get_db()

@router.post("", status_code=201)
async def create_report(report: Report):
    """Submit a new issue report"""
    try:
        report_dict = report.model_dump(exclude={'id'})
        report_dict['createdAt'] = datetime.now()
        report_dict['status'] = 'pending'
        
        doc_ref = db.collection('reports').document()
        doc_ref.set(report_dict)
        
        return {"id": doc_ref.id, "message": "Report submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[dict])
async def get_all_reports():
    """Get all reports (admin endpoint)"""
    try:
        reports_ref = db.collection('reports')
        docs = reports_ref.stream()
        reports_list = []
        for doc in docs:
            report_data = doc.to_dict()
            report_data['id'] = doc.id
            reports_list.append(report_data)
        return reports_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report_by_id(report_id: str):
    """Get report by ID"""
    try:
        doc = db.collection('reports').document(report_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        report_data = doc.to_dict()
        report_data['id'] = doc.id
        return report_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
