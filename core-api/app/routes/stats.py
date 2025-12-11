from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from typing import Dict, Any

router = APIRouter(prefix="/api/stats", tags=["stats"])
db = get_db()

@router.get("")
async def get_statistics() -> Dict[str, Any]:
    """
    Get platform statistics from Firestore
    
    Returns:
    - totalDonations: Sum of all donations (or from fund_stats)
    - totalDonors: Number of unique donors
    - totalProjects: Number of projects
    - activeProjects: Number of active projects
    """
    try:
        # First check if fund_stats exists (pre-configured stats)
        fund_stats_ref = db.collection('fund_stats').document('current')
        fund_stats_doc = fund_stats_ref.get()
        
        if fund_stats_doc.exists:
            # Use pre-configured stats
            stats_data = fund_stats_doc.to_dict()
            return {
                "status": "success",
                "data": {
                    "totalDonations": stats_data.get('totalDonations', 0),
                    "totalDonors": stats_data.get('totalDonors', 0),
                    "totalProjects": stats_data.get('totalProjects', 0),
                    "activeProjects": stats_data.get('activeProjects', 0)
                }
            }
        
        # Otherwise calculate from actual collections
        # Get total donations
        donations_ref = db.collection('donations')
        donations = donations_ref.stream()
        total_donations = 0
        for donation in donations:
            donation_data = donation.to_dict()
            total_donations += donation_data.get('amount', 0)
        
        # Get total donors
        donors_ref = db.collection('donors')
        donors = list(donors_ref.stream())
        total_donors = len(donors)
        
        # Get projects stats
        projects_ref = db.collection('projects')
        projects = list(projects_ref.stream())
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.to_dict().get('status') == 'active')
        
        return {
            "status": "success",
            "data": {
                "totalDonations": total_donations,
                "totalDonors": total_donors,
                "totalProjects": total_projects,
                "activeProjects": active_projects
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
