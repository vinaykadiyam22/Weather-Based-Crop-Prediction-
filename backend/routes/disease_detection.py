from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from services.disease_detection import detect_disease
from services.gemini_service import generate_disease_advisory
from services.email_service import email_service
from models.user import User

router = APIRouter(prefix="/api/disease", tags=["Disease Detection"])

class DiseaseDetectionResponse(BaseModel):
    crop_name: str
    disease_name: str
    confidence: float
    is_healthy: bool
    advisory: str
    all_predictions: dict

@router.post("/detect", response_model=DiseaseDetectionResponse)
async def detect_crop_disease(
    image: UploadFile = File(...),
    user_id: int = Form(None),
    send_email: bool = Form(False),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    """
    Detect disease from uploaded crop image
    Returns disease name, confidence, and Gemini-generated advisory
    """
    # Validate image
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        # Detect disease using pretrained model
        detection_result = detect_disease(image_bytes)
        
        # Get user (for language and email)
        uid = int(user_id) if user_id and str(user_id).isdigit() else None
        user = db.query(User).filter(User.id == uid).first() if uid else None
        # Prefer explicit language from form, then user profile
        user_lang = (language if language else (user.language if user and user.language else None)) or "en"

        # Generate advisory using Gemini (crop, disease, confidence → human-like suggestions)
        advisory = generate_disease_advisory(
            disease_name=detection_result['disease_name'],
            confidence=detection_result['confidence'],
            crop_name=detection_result.get('crop_name', 'crop'),
            language=user_lang
        )

        # Send email if requested and user exists
        if send_email and user and not detection_result['is_healthy']:
            email_service.send_disease_alert(
                to_email=user.email,
                disease_name=detection_result['disease_name'],
                advisory=advisory,
                name=user.name,
                crop_name=detection_result.get('crop_name')
            )
        
        return {
            "crop_name": detection_result.get('crop_name', 'Unknown'),
            "disease_name": detection_result['disease_name'],
            "confidence": detection_result['confidence'],
            "is_healthy": detection_result['is_healthy'],
            "advisory": advisory,
            "all_predictions": detection_result['all_predictions']
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease detection failed: {str(e)}")
