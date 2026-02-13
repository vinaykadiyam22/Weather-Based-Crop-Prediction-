from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.soil_analysis_history import SoilAnalysisHistory
from models.user import User
from services.gemini_service import generate_soil_type_explanation, generate_soil_analysis_explanation
from services.soil_detection import detect_soil_type
from datetime import datetime

router = APIRouter(prefix="/api/soil", tags=["Soil Analysis"])

# Manual soil type selection (no ML required)
SOIL_TYPES = [
    "Clay", "Sandy", "Loamy", "Silty", "Peaty", 
    "Chalky", "Red Soil", "Black Soil", "Alluvial"
]

SOIL_CHARACTERISTICS = {
    "Clay": {
        "water_retention": "High",
        "drainage": "Poor",
        "nutrient_retention": "High",
        "workability": "Difficult when wet"
    },
    "Sandy": {
        "water_retention": "Low",
        "drainage": "Excellent",
        "nutrient_retention": "Low",
        "workability": "Easy"
    },
    "Loamy": {
        "water_retention": "Good",
        "drainage": "Good",
        "nutrient_retention": "Good",
        "workability": "Easy"
    },
    "Silty": {
        "water_retention": "Good",
        "drainage": "Moderate",
        "nutrient_retention": "Good",
        "workability": "Moderate"
    },
    "Black Soil": {
        "water_retention": "Very High",
        "drainage": "Poor",
        "nutrient_retention": "High",
        "workability": "Difficult",
        "best_for": "Cotton, Sugarcane"
    },
    "Red Soil": {
        "water_retention": "Moderate",
        "drainage": "Good",
        "nutrient_retention": "Moderate",
        "workability": "Easy",
        "best_for": "Millets, Groundnut"
    },
    "Alluvial": {
        "water_retention": "Good",
        "drainage": "Good",
        "nutrient_retention": "Excellent",
        "workability": "Easy",
        "best_for": "Rice, Wheat, Sugarcane"
    }
}

class SoilTypeSelectionRequest(BaseModel):
    user_id: int
    soil_type: str  # Manual selection from dropdown
    location: str = None
    language: str = None  # Override user language for advisory generation

class SoilTypeResponse(BaseModel):
    soil_type: str
    characteristics: dict
    explanation: str

@router.get("/types")
def get_soil_types():
    """Get list of available soil types for manual selection"""
    return {"soil_types": SOIL_TYPES}


@router.post("/detect-from-image")
async def detect_soil_from_image(
    image: UploadFile = File(...),
    user_id: int = Form(None),
    language: str = Form("en"),
    location: str = Form(None),
    db: Session = Depends(get_db),
):
    """Detect soil type from uploaded soil image. User uploads image, system identifies soil type."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    try:
        image_bytes = await image.read()
        result = detect_soil_type(image_bytes)
        uid = int(user_id) if user_id and str(user_id).isdigit() else None
        user = db.query(User).filter(User.id == uid).first() if uid else None
        lang = (language if language else (user.language if user and user.language else None)) or "en"
        characteristics = result.get("characteristics", {})
        explanation = generate_soil_type_explanation(
            soil_type=result["soil_type"],
            characteristics=characteristics,
            language=lang,
        )
        return {
            "soil_type": result["soil_type"],
            "confidence": result.get("confidence", 0),
            "characteristics": characteristics,
            "explanation": explanation,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Soil detection failed: {str(e)}")

@router.post("/select-type", response_model=SoilTypeResponse)
def select_soil_type(request: SoilTypeSelectionRequest, db: Session = Depends(get_db)):
    """Manual soil type selection with Gemini explanation"""
    if request.soil_type not in SOIL_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid soil type. Choose from: {', '.join(SOIL_TYPES)}")
    
    # Get characteristics
    characteristics = SOIL_CHARACTERISTICS.get(request.soil_type, {
        "water_retention": "Varies",
        "drainage": "Varies",
        "nutrient_retention": "Varies",
        "workability": "Varies"
    })

    user = db.query(User).filter(User.id == request.user_id).first() if request.user_id else None
    lang = (request.language or (user.language if user and user.language else None)) or "en"

    # Generate Gemini explanation (with user language)
    explanation = generate_soil_type_explanation(
        soil_type=request.soil_type,
        characteristics=characteristics,
        language=lang
    )
    
    return {
        "soil_type": request.soil_type,
        "characteristics": characteristics,
        "explanation": explanation
    }

class SoilAnalysisRequest(BaseModel):
    user_id: int
    soil_type: str = None  # Optional manual soil type
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    organic_matter: float = None
    location: str = None
    language: str = None  # Override user language for advisory generation

class SoilAnalysisResponse(BaseModel):
    analysis_id: int
    soil_parameters: dict
    soil_health: str
    fertilizer_recommendations: list
    explanation: str

@router.post("/analyze", response_model=SoilAnalysisResponse)
def analyze_soil(request: SoilAnalysisRequest, db: Session = Depends(get_db)):
    """Analyze soil parameters, save to history, and provide recommendations"""
    
    # Determine soil health
    soil_health = "good"
    if request.ph < 5.5 or request.ph > 8.0:
        soil_health = "poor"
    elif request.ph < 6.0 or request.ph > 7.5:
        soil_health = "medium"
    
    # Determine fertilizer needs based on NPK values
    fertilizers = []
    
    if request.nitrogen < 200:
        fertilizers.append("Urea or Ammonium Sulfate (Nitrogen)")
    if request.phosphorus < 20:
        fertilizers.append("Superphosphate or DAP (Phosphorus)")
    if request.potassium < 150:
        fertilizers.append("Muriate of Potash (Potassium)")
    
    if not fertilizers:
        fertilizers.append("Balanced NPK fertilizer for maintenance")
    
    # Add pH correction if needed
    if request.ph < 6.0:
        fertilizers.append("Lime (to increase pH)")
    elif request.ph > 7.5:
        fertilizers.append("Sulfur or Organic matter (to decrease pH)")

    user = db.query(User).filter(User.id == request.user_id).first() if request.user_id else None
    lang = (request.language or (user.language if user and user.language else None)) or "en"

    # Generate Gemini explanation (with user language)
    explanation = generate_soil_analysis_explanation(
        soil_params={
            "nitrogen": request.nitrogen,
            "phosphorus": request.phosphorus,
            "potassium": request.potassium,
            "ph": request.ph,
            "organic_matter": request.organic_matter,
            "soil_type": request.soil_type
        },
        fertilizer_recommendations=fertilizers,
        language=lang
    )
    
    # Save to history
    soil_analysis = SoilAnalysisHistory(
        user_id=request.user_id,
        soil_type=request.soil_type,
        nitrogen=request.nitrogen,
        phosphorus=request.phosphorus,
        potassium=request.potassium,
        ph=request.ph,
        organic_matter=request.organic_matter,
        soil_health=soil_health,
        fertilizer_recommendations=fertilizers,
        gemini_advisory=explanation,
        location=request.location or "Unknown",
        analysis_date=datetime.utcnow()
    )
    
    db.add(soil_analysis)
    db.commit()
    db.refresh(soil_analysis)
    
    return {
        "analysis_id": soil_analysis.id,
        "soil_parameters": {
            "soil_type": request.soil_type,
            "nitrogen": request.nitrogen,
            "phosphorus": request.phosphorus,
            "potassium": request.potassium,
            "ph": request.ph,
            "organic_matter": request.organic_matter
        },
        "soil_health": soil_health,
        "fertilizer_recommendations": fertilizers,
        "explanation": explanation
    }

@router.get("/history/{user_id}")
def get_soil_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get soil analysis history for a user"""
    analyses = db.query(SoilAnalysisHistory)\
        .filter(SoilAnalysisHistory.user_id == user_id)\
        .order_by(SoilAnalysisHistory.analysis_date.desc())\
        .limit(limit)\
        .all()
    
    return {
        "total": len(analyses),
        "analyses": [
            {
                "id": analysis.id,
                "date": analysis.analysis_date,
                "soil_type": analysis.soil_type,
                "soil_health": analysis.soil_health,
                "npk": {
                    "nitrogen": analysis.nitrogen,
                    "phosphorus": analysis.phosphorus,
                    "potassium": analysis.potassium
                },
                "ph": analysis.ph,
                "location": analysis.location
            }
            for analysis in analyses
        ]
    }
