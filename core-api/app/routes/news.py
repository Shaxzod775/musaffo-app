from fastapi import APIRouter, HTTPException
from app.config.firebase import get_db
from app.models.models import News
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/news", tags=["news"])
db = get_db()

@router.get("", response_model=List[dict])
async def get_all_news():
    """Get all news articles"""
    try:
        news_ref = db.collection('news')
        docs = news_ref.stream()
        news_list = []
        for doc in docs:
            news_data = doc.to_dict()
            news_data['id'] = doc.id
            news_list.append(news_data)
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{news_id}")
async def get_news_by_id(news_id: str):
    """Get single news article by ID"""
    try:
        doc = db.collection('news').document(news_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="News not found")
        news_data = doc.to_dict()
        news_data['id'] = doc.id
        return news_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", status_code=201)
async def create_news(news: News):
    """Create new news article"""
    try:
        news_dict = news.model_dump(exclude={'id'})
        news_dict['createdAt'] = datetime.now()
        news_dict['timestamp'] = datetime.now()
        
        doc_ref = db.collection('news').document()
        doc_ref.set(news_dict)
        
        return {"id": doc_ref.id, "message": "News created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
