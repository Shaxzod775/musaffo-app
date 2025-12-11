"""
Complaints AI Service - FastAPI Application
Analyzes environmental violation photos using Claude Haiku AI
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv

from agent import get_agent
from firebase_client import get_firebase
from knowledge_base import get_all_violations_summary, get_violation_info, VIOLATIONS

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Complaints AI Service",
    description="AI-powered environmental violation analysis service for Uzbekistan",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://air-quality-eco-fund-2.vercel.app",
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "service": "Complaints AI Service",
        "version": "1.0.0",
        "description": "Анализ экологических нарушений с помощью ИИ",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/analyze-complaint")
async def analyze_complaint(
    images: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    address: Optional[str] = Form(None)
):
    """
    Analyze uploaded images for environmental violations

    - **images**: Photos of the potential violation (JPEG, PNG) - minimum 3, maximum 10
    - **description**: Description from the complainant
    - **address**: Address where the violation occurred

    Returns analysis with violation type, estimated fine, potential reward, and spam check
    """
    logger.info(f"Received complaint analysis request - Images: {len(images)}, Description length: {len(description) if description else 0}, Address: {address}")

    # Validate minimum/maximum photos
    if len(images) < 3:
        logger.warning(f"Too few images: {len(images)}")
        raise HTTPException(
            status_code=400,
            detail="Минимум 3 фото обязательны для подачи жалобы"
        )

    if len(images) > 10:
        logger.warning(f"Too many images: {len(images)}")
        raise HTTPException(
            status_code=400,
            detail="Максимум 10 фото можно загрузить"
        )

    # Validate file types and read image data
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    images_data = []

    for i, image in enumerate(images):
        if image.content_type not in allowed_types:
            logger.warning(f"Invalid file type rejected for image {i}: {image.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Неверный тип файла для изображения {i+1}. Разрешены: {', '.join(allowed_types)}"
            )

        image_bytes = await image.read()
        images_data.append({
            "data": image_bytes,
            "type": image.content_type,
            "filename": image.filename
        })
        logger.info(f"Image {i+1} read: {len(image_bytes)} bytes")

    # Analyze with Claude Haiku (using all images)
    logger.info("Starting AI analysis with Claude Haiku")
    agent = get_agent()
    analysis_result = await agent.analyze_images(
        images_data=images_data,
        description=description,
        address=address
    )
    logger.info(f"AI analysis completed - Violation detected: {analysis_result.get('violation_detected', False)}, Is spam: {analysis_result.get('is_spam', False)}")

    # If spam detected, return early with spam flag
    if analysis_result.get('is_spam', False):
        logger.warning("Spam detected, rejecting complaint")
        return JSONResponse(content={
            "success": False,
            "is_spam": True,
            "spam_reason": analysis_result.get('spam_reason', 'Обнаружен спам или нерелевантный контент'),
            "violation_detected": False
        })

    # Save to Firebase
    try:
        logger.info("Saving complaint to Firebase")
        firebase = get_firebase()
        complaint_id = await firebase.save_complaint(
            analysis_result=analysis_result,
            user_description=description,
            address=address,
            images_count=len(images)
        )
        analysis_result["complaint_id"] = complaint_id
        logger.info(f"Complaint saved successfully with ID: {complaint_id}")
    except Exception as e:
        logger.error(f"Failed to save to Firebase: {str(e)}")
        # Continue without saving if Firebase fails
        analysis_result["storage_error"] = str(e)

    logger.info("Returning analysis result to client")
    return JSONResponse(content=analysis_result)


@app.get("/complaints/{complaint_id}")
async def get_complaint(complaint_id: str):
    """Get a specific complaint by ID"""
    logger.info(f"Fetching complaint with ID: {complaint_id}")
    firebase = get_firebase()
    complaint = await firebase.get_complaint(complaint_id)
    
    if not complaint:
        logger.warning(f"Complaint not found: {complaint_id}")
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    logger.info(f"Complaint retrieved successfully: {complaint_id}")
    return complaint


@app.get("/complaints")
async def list_complaints(limit: int = 50):
    """List all complaints"""
    firebase = get_firebase()
    complaints = await firebase.get_all_complaints(limit=limit)
    return {"complaints": complaints, "count": len(complaints)}


@app.post("/complaints/batch")
async def get_complaints_batch(complaint_ids: list[str]):
    """Get multiple complaints by their IDs"""
    logger.info(f"Fetching batch of {len(complaint_ids)} complaints")
    firebase = get_firebase()
    complaints = await firebase.get_complaints_by_ids(complaint_ids)
    logger.info(f"Found {len(complaints)} complaints out of {len(complaint_ids)} requested")
    return {"complaints": complaints, "count": len(complaints)}


@app.get("/violations")
async def list_violations():
    """Get list of all violation types with fines"""
    violations_list = []
    
    for key, v in VIOLATIONS.items():
        violations_list.append({
            "type": key,
            "name_ru": v["name_ru"],
            "name_en": v["name_en"],
            "description": v["description_ru"],
            "fine_min": v["fine_min"],
            "fine_max": v["fine_max"],
            "fine_min_formatted": f"{v['fine_min']:,}".replace(",", " ") + " сум",
            "fine_max_formatted": f"{v['fine_max']:,}".replace(",", " ") + " сум"
        })
    
    return {"violations": violations_list}


@app.get("/violations/{violation_type}")
async def get_violation(violation_type: str):
    """Get detailed info about a specific violation type"""
    info = get_violation_info(violation_type)
    
    if not info:
        raise HTTPException(
            status_code=404, 
            detail=f"Violation type '{violation_type}' not found"
        )
    
    return info


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
