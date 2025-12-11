from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from app.models.models import Donation
from datetime import datetime
from typing import List
from google.cloud import firestore

router = APIRouter(prefix="/api/donations", tags=["donations"])
db = get_db()

@router.post("", status_code=201)
async def create_donation(donation: Donation):
    """Create new donation"""
    try:
        donation_dict = donation.model_dump(exclude={'id'})
        donation_dict['createdAt'] = datetime.now()
        donation_dict['updatedAt'] = datetime.now()
        
        # Create donation record
        doc_ref = db.collection('donations').document()
        doc_ref.set(donation_dict)
        
        # Update donor's total donated amount in 'donors' collection
        donor_ref = db.collection('donors').document(donation.userId)
        donor_doc = donor_ref.get()
        
        if donor_doc.exists:
            # Increment existing donor's total
            donor_ref.update({
                'totalDonated': firestore.Increment(donation.amount),
                'lastDonation': datetime.now()
            })
        else:
            # Create new donor record
            donor_ref.set({
                'userId': donation.userId,
                'totalDonated': donation.amount,
                'projectContributions': {},
                'lastDonation': datetime.now(),
                'createdAt': datetime.now()
            })
        
        # Update fund_stats
        fund_stats_ref = db.collection('fund_stats').document('global')
        fund_stats_doc = fund_stats_ref.get()
        
        if fund_stats_doc.exists:
            # Increment totalDonations and totalDonors
            fund_stats_ref.update({
                'totalDonations': firestore.Increment(donation.amount),
                'totalDonors': firestore.Increment(1),
                'lastUpdated': datetime.now()
            })
        else:
            # Create fund_stats if doesn't exist
            fund_stats_ref.set({
                'totalDonations': donation.amount,
                'totalDonors': 1,
                'totalProjects': 0,
                'activeProjects': 0,
                'lastUpdated': datetime.now()
            })
        
        return {"id": doc_ref.id, "message": "Donation created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[dict])
async def get_all_donations():
    """Get all donations"""
    try:
        donations_ref = db.collection('donations')
        docs = donations_ref.stream()
        donations_list = []
        for doc in docs:
            donation_data = doc.to_dict()
            donation_data['id'] = doc.id
            donations_list.append(donation_data)
        return donations_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/donor/{user_id}")
async def get_donor_info(user_id: str):
    """Get donor information including total donated and project contributions"""
    try:
        doc = db.collection('donors').document(user_id).get()
        if not doc.exists:
            return {
                "userId": user_id,
                "isContributor": False, 
                "totalDonated": 0,
                "projectContributions": {}
            }
        donor_data = doc.to_dict()
        donor_data['id'] = doc.id
        donor_data['isContributor'] = True
        return donor_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/donor/{user_id}/distribute")
async def distribute_donation_to_projects(user_id: str, request: dict):
    """Distribute a donation evenly to active projects and save to donor record"""
    try:
        donation_amount = request.get('donationAmount')
        project_ids = request.get('projectIds', [])
        
        donor_ref = db.collection('donors').document(user_id)
        donor_doc = donor_ref.get()
        
        # Calculate amount per project
        amount_per_project = donation_amount // len(project_ids) if len(project_ids) > 0 else 0
        
        # Get existing contributions
        if donor_doc.exists:
            donor_data = donor_doc.to_dict()
            project_contributions = donor_data.get('projectContributions', {})
        else:
            project_contributions = {}
        
        # Update contributions for each project
        for project_id in project_ids:
            if project_id in project_contributions:
                project_contributions[project_id] += amount_per_project
            else:
                project_contributions[project_id] = amount_per_project
        
        # Update donor record with new project contributions
        donor_ref.update({
            'projectContributions': project_contributions,
            'lastDonation': datetime.now()
        })
        
        return {
            "message": "Donation distributed successfully",
            "amountPerProject": amount_per_project,
            "projectContributions": project_contributions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
