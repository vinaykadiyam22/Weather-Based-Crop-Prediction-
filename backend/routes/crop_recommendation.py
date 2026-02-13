from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from database import get_db
from sqlalchemy.orm import Session
from models.user import User
from services.crop_recommendation import get_crop_recommendations, get_all_crops, search_crops

router = APIRouter(prefix="/api/crop", tags=["Crop Recommendation"])


class SoilAnalysisInput(BaseModel):
    """Optional soil analysis parameters for data-driven recommendations."""
    soil_type: Optional[str] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    organic_matter: Optional[float] = None
    soil_health: Optional[str] = None


class CropRecommendationRequest(BaseModel):
    soil_type: str
    location: str
    season: str = None
    temperature: float = None
    user_id: int = None
    language: str = None
    soil_analysis: Optional[SoilAnalysisInput] = None


class CropInfo(BaseModel):
    name: str
    local_name: str
    score: int
    growing_duration: str
    rainfall_min: int


class CropRecommendationResponse(BaseModel):
    recommended_crops: List
    explanation: str
    total_recommendations: int


@router.post("/recommend", response_model=CropRecommendationResponse)
def recommend_crops(request: CropRecommendationRequest, db: Session = Depends(get_db)):
    """
    Get crop recommendations using multi-factor analysis:
    soil, weather forecast, location, season, market trends, climate alerts.
    Pass soil_analysis or user_id for richer context.
    """
    lang = request.language
    if not lang and request.user_id:
        user = db.query(User).filter(User.id == request.user_id).first()
        if user and user.language:
            lang = user.language
    lang = lang or "en"

    soil_analysis_dict = None
    if request.soil_analysis:
        soil_analysis_dict = request.soil_analysis.model_dump(exclude_none=True)
        if request.soil_analysis.soil_type:
            soil_analysis_dict["soil_type"] = request.soil_analysis.soil_type

    result = get_crop_recommendations(
        soil_type=request.soil_type,
        location=request.location,
        season=request.season,
        temperature=request.temperature,
        language=lang,
        soil_analysis=soil_analysis_dict,
        user_id=request.user_id,
        db=db,
    )
    return result

@router.get("/all")
def list_all_crops():
    """Get all available crops"""
    return {"crops": get_all_crops()}

@router.get("/search")
def search(query: str = Query(..., min_length=2)):
    """Search crops by name"""
    results = search_crops(query)
    return {"results": results, "count": len(results)}
