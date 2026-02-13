from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from models.user import User
from models.soil_analysis_history import SoilAnalysisHistory
from models.crop_history import CropHistory
from models.current_crop import CurrentCrop
from models.alert import Alert
from models.market_price import MarketPrice
from datetime import datetime, timedelta

def get_user_farming_context(db: Session, user_id: int) -> Dict:
    """
    Get complete farming context for a user to provide AI with comprehensive information
    
    This context is used by:
    - Crop recommendations (considers history, soil, market)
    - Enhanced Gemini prompts (personalized advice)
    - Dashboard insights
    
    Returns:
        Dictionary with user's complete farming profile and history
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Get latest soil analysis
    latest_soil = db.query(SoilAnalysisHistory)\
        .filter(SoilAnalysisHistory.user_id == user_id)\
        .order_by(SoilAnalysisHistory.analysis_date.desc())\
        .first()
    
    # Get soil analysis history (last 5)
    soil_history = db.query(SoilAnalysisHistory)\
        .filter(SoilAnalysisHistory.user_id == user_id)\
        .order_by(SoilAnalysisHistory.analysis_date.desc())\
        .limit(5)\
        .all()
    
    # Get crop history (last 10 seasons)
    crop_history = db.query(CropHistory)\
        .filter(CropHistory.user_id == user_id)\
        .order_by(CropHistory.planting_date.desc())\
        .limit(10)\
        .all()
    
    # Get current crops
    current_crops = db.query(CurrentCrop)\
        .filter(CurrentCrop.user_id == user_id)\
        .all()
    
    # Get active alerts (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    active_alerts = db.query(Alert)\
        .filter(Alert.user_id == user_id)\
        .filter(Alert.created_at >= seven_days_ago)\
        .order_by(Alert.created_at.desc())\
        .all()
    
    # Get market trends (top 10 crops by recent price increase)
    # This is a simplified version - in production, implement proper trend analysis
    recent_prices = db.query(MarketPrice)\
        .order_by(MarketPrice.date.desc())\
        .limit(100)\
        .all()
    
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "location": user.location,
            "language": user.language,
            "farm_size": user.farm_size,
            "farming_experience": user.farming_experience,
            "preferred_crops": user.preferred_crops or []
        },
        "latest_soil_analysis": {
            "soil_type": latest_soil.soil_type if latest_soil else None,
            "nitrogen": latest_soil.nitrogen if latest_soil else None,
            "phosphorus": latest_soil.phosphorus if latest_soil else None,
            "potassium": latest_soil.potassium if latest_soil else None,
            "ph": latest_soil.ph if latest_soil else None,
            "health": latest_soil.soil_health if latest_soil else None,
            "date": latest_soil.analysis_date if latest_soil else None
        } if latest_soil else None,
        "soil_history": [
            {
                "date": analysis.analysis_date,
                "soil_type": analysis.soil_type,
                "health": analysis.soil_health,
                "npk": {
                    "n": analysis.nitrogen,
                    "p": analysis.phosphorus,
                    "k": analysis.potassium
                }
            }
            for analysis in soil_history
        ],
        "crop_history": [
            {
                "crop_name": crop.crop_name,
                "season": crop.season,
                "planting_date": crop.planting_date,
                "yield": crop.yield_amount,
                "status": crop.status.value
            }
            for crop in crop_history
        ],
        "current_crops": [
            {
                "crop_name": crop.crop_name,
                "planting_date": crop.planting_date,
                "health_status": crop.health_status,
                "field_size": crop.field_size
            }
            for crop in current_crops
        ],
        "active_alerts": [
            {
                "title": alert.title,
                "severity": alert.severity,
                "date": alert.created_at
            }
            for alert in active_alerts
        ],
        "market_trends": _analyze_market_trends(recent_prices) if recent_prices else []
    }

def _analyze_market_trends(prices: List[MarketPrice]) -> List[Dict]:
    """
    Analyze market price trends
    Simple implementation - group by crop and calculate trend
    """
    from collections import defaultdict
    
    crop_prices = defaultdict(list)
    for price in prices:
        crop_prices[price.crop_name].append(price.price)
    
    trends = []
    for crop, price_list in crop_prices.items():
        if len(price_list) >= 2:
            recent_avg = sum(price_list[:5]) / min(5, len(price_list))
            older_avg = sum(price_list[5:10]) / min(5, len(price_list[5:10])) if len(price_list) > 5 else recent_avg
            
            change = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            if change > 5:  # Only include crops with significant price increase
                trends.append({
                    "crop": crop,
                    "trend": "up",
                    "change_percent": round(change, 1),
                    "current_price": round(recent_avg, 2)
                })
    
    # Sort by change percentage (highest first)
    trends.sort(key=lambda x: x['change_percent'], reverse=True)
    return trends[:10]  # Top 10 trending crops

def get_recent_crop_names(db: Session, user_id: int, limit: int = 3) -> List[str]:
    """Get list of recently grown crops to avoid in recommendations (crop rotation)"""
    recent_crops = db.query(CropHistory.crop_name)\
        .filter(CropHistory.user_id == user_id)\
        .order_by(CropHistory.planting_date.desc())\
        .limit(limit)\
        .all()
    
    return [crop[0] for crop in recent_crops]
