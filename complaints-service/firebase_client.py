"""
Firebase client for storing complaint analysis results
"""

import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Optional
import uuid

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Firebase Firestore client for complaints storage"""
    
    def __init__(self):
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase connection"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            logger.info("Firebase app already initialized")
        except ValueError:
            logger.info("Initializing new Firebase app")
            # Initialize with credentials
            cred_path = os.getenv('FIREBASE_CREDENTIALS', './firebase-credentials.json')
            
            if os.path.exists(cred_path):
                logger.info(f"Loading Firebase credentials from: {cred_path}")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                logger.warning(f"Credentials file not found at {cred_path}, using default service account")
                # Try to initialize without credentials (for Cloud Run with default service account)
                firebase_admin.initialize_app()
        
        self.db = firestore.client()
        logger.info("Firebase Firestore client initialized")
    
    async def save_complaint(
        self,
        analysis_result: dict,
        user_description: Optional[str] = None,
        image_url: Optional[str] = None,
        address: Optional[str] = None,
        images_count: int = 0
    ) -> str:
        """
        Save a complaint analysis result to Firestore

        Args:
            analysis_result: The AI analysis result
            user_description: Optional user-provided description
            image_url: Optional URL to the stored image
            address: Address where violation occurred
            images_count: Number of images submitted

        Returns:
            The complaint ID
        """
        complaint_id = str(uuid.uuid4())

        logger.info(f"Saving complaint with ID: {complaint_id}")

        complaint_data = {
            "id": complaint_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",  # pending, confirmed, rejected
            "user_description": user_description,
            "address": address,
            "images_count": images_count,
            "image_url": image_url,
            "analysis": {
                "success": analysis_result.get("success", False),
                "violation_detected": analysis_result.get("violation_detected", False),
                "violation_type": analysis_result.get("violation_type"),
                "violation_name": analysis_result.get("violation_name"),
                "severity": analysis_result.get("severity"),
                "fine_range": analysis_result.get("fine_range"),
                "reward_range": analysis_result.get("reward_range"),
                "raw_analysis": analysis_result.get("raw_analysis")
            }
        }

        # Save to Firestore
        self.db.collection("complaints").document(complaint_id).set(complaint_data)
        logger.info(f"Complaint saved successfully: {complaint_id}")

        return complaint_id
    
    async def get_complaint(self, complaint_id: str) -> Optional[dict]:
        """Get a complaint by ID"""
        doc = self.db.collection("complaints").document(complaint_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def get_all_complaints(self, limit: int = 50) -> list:
        """Get all complaints, ordered by creation date"""
        docs = (
            self.db.collection("complaints")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        
        return [doc.to_dict() for doc in docs]
    
    async def get_complaints_by_ids(self, complaint_ids: list) -> list:
        """Get complaints by list of IDs"""
        if not complaint_ids:
            return []
        
        complaints = []
        for complaint_id in complaint_ids:
            doc = self.db.collection("complaints").document(complaint_id).get()
            if doc.exists:
                complaints.append(doc.to_dict())
        
        # Sort by created_at descending
        complaints.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return complaints
    
    async def update_complaint_status(
        self, 
        complaint_id: str, 
        status: str,
        reward_paid: Optional[int] = None
    ) -> bool:
        """Update complaint status"""
        doc_ref = self.db.collection("complaints").document(complaint_id)
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if reward_paid is not None:
            update_data["reward_paid"] = reward_paid
        
        try:
            doc_ref.update(update_data)
            return True
        except Exception:
            return False


# Singleton instance
_firebase_instance = None

def get_firebase() -> FirebaseClient:
    """Get or create the Firebase client instance"""
    global _firebase_instance
    if _firebase_instance is None:
        _firebase_instance = FirebaseClient()
    return _firebase_instance
