from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from app.models.models import Voting, VoteRecord
from datetime import datetime
from typing import List
from google.cloud import firestore

router = APIRouter(prefix="/api/voting", tags=["voting"])
db = get_db()

@router.get("", response_model=List[dict])
async def get_all_voting():
    """Get all voting initiatives"""
    try:
        voting_ref = db.collection('voting')
        docs = voting_ref.stream()
        voting_list = []
        for doc in docs:
            voting_data = doc.to_dict()
            voting_data['id'] = doc.id
            voting_list.append(voting_data)
        return voting_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{voting_id}")
async def get_voting_by_id(voting_id: str):
    """Get voting details by ID"""
    try:
        doc = db.collection('voting').document(voting_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Voting not found")
        voting_data = doc.to_dict()
        voting_data['id'] = doc.id
        return voting_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{voting_id}/vote")
async def submit_vote(voting_id: str, user_id: str, vote: str):
    """Submit a vote (up or down)"""
    try:
        if vote not in ['up', 'down']:
            raise HTTPException(status_code=400, detail="Vote must be 'up' or 'down'")
        
        voting_ref = db.collection('voting').document(voting_id)
        voting_doc = voting_ref.get()
        
        if not voting_doc.exists:
            raise HTTPException(status_code=404, detail="Voting not found")
        
        voting_data = voting_doc.to_dict()
        voters = voting_data.get('voters', [])
        
        # Check if user already voted
        existing_vote = next((v for v in voters if v['userId'] == user_id), None)
        if existing_vote:
            raise HTTPException(status_code=400, detail="User already voted")
        
        # Add vote
        voters.append({'userId': user_id, 'vote': vote})
        
        # Update counts
        if vote == 'up':
            voting_ref.update({
                'votesFor': firestore.Increment(1),
                'voters': voters
            })
        else:
            voting_ref.update({
                'votesAgainst': firestore.Increment(1),
                'voters': voters
            })
        
        return {"message": "Vote submitted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
