from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from services.weather_service import weather_service
from services.climate_alert import climate_alert_service
from models.user import User
from typing import List

router = APIRouter(prefix="/api/weather", tags=["Weather & Climate"])

class WeatherRequest(BaseModel):
    location: str
    lat: float = None
    lon: float = None


class SyncAlertsRequest(BaseModel):
    user_id: int
    location: str = None  # Falls back to user.location if not provided
    lat: float = None
    lon: float = None

@router.post("/current")
def get_current_weather(request: WeatherRequest):
    """Get current weather data"""
    weather = weather_service.get_current_weather(
        request.location,
        request.lat,
        request.lon
    )
    return weather

@router.post("/forecast")
def get_forecast(request: WeatherRequest, days: int = 5):
    """Get weather forecast"""
    forecast = weather_service.get_forecast(
        request.location,
        request.lat,
        request.lon,
        days
    )
    return forecast

@router.post("/check-alerts")
def check_alerts(request: WeatherRequest):
    """Check for weather-related alerts"""
    alerts = climate_alert_service.check_weather_alerts(
        location=request.location,
        lat=request.lat,
        lon=request.lon
    )
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "has_critical": any(a.get('severity') == 'critical' or a.get('severity') == 'high' for a in alerts)
    }


@router.post("/sync-alerts")
def sync_alerts(request: SyncAlertsRequest, db: Session = Depends(get_db)):
    """
    Check weather for risks, create persisted alerts in DB, send emails.
    Deduplicates: avoids creating same alert type within 24h for same user.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = climate_alert_service.sync_weather_alerts(
        db=db,
        user_id=request.user_id,
        location=request.location or user.location,
        user_email=user.email,
        user_name=user.name,
        language=user.language or "en"
    )
    return result

class CreateAlertRequest(BaseModel):
    user_id: int
    alert_type: str
    severity: str
    title: str
    description: str
    location: str
    send_email: bool = True

@router.post("/alerts/create")
def create_alert(request: CreateAlertRequest, db: Session = Depends(get_db)):
    """Create a climate alert with advisory"""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    alert = climate_alert_service.create_alert_with_advisory(
        db=db,
        user_id=request.user_id,
        alert_type=request.alert_type,
        severity=request.severity,
        title=request.title,
        description=request.description,
        location=request.location,
        send_email=request.send_email,
        user_email=user.email,
        user_name=user.name,
        language=user.language or "en"
    )
    
    return {
        "id": alert.id,
        "title": alert.title,
        "severity": alert.severity.value,
        "recommendations": alert.recommendations
    }

# Manual weather selection scenarios for demo
WEATHER_SCENARIOS = {
    "heavy_rain": {
        "alert_type": "Heavy Rainfall",
        "severity": "high",
        "title": "Heavy Rainfall Warning",
        "description": "Heavy to very heavy rainfall expected in your area over the next 24-48 hours"
    },
    "drought": {
        "alert_type": "Drought",
        "severity": "critical",
        "title": "Severe Drought Alert",
        "description": "Severe water scarcity conditions detected. Immediate conservation measures required"
    },
    "heatwave": {
        "alert_type": "Heat Wave",
        "severity": "high",
        "title": "Extreme Heat Warning",
        "description": "Temperatures expected to reach 42-45°C. Take precautions to protect crops"
    },
    "frost": {
        "alert_type": "Frost",
        "severity": "medium",
        "title": "Frost Alert",
        "description": "Temperature may drop below freezing point. Protect sensitive crops"
    },
    "cyclone": {
        "alert_type": "Cyclone",
        "severity": "critical",
        "title": "Cyclone Warning",
        "description": "Cyclonic storm approaching. Secure all equipment and prepare for heavy winds"
    },
    "flood": {
        "alert_type": "Flood",
        "severity": "high",
        "title": "Flood Warning",
        "description": "Water logging and flooding expected in low-lying areas"
    }
}

class ManualWeatherTriggerRequest(BaseModel):
    user_id: int
    weather_scenario: str  # One of: heavy_rain, drought, heatwave, frost, cyclone, flood

@router.post("/demo/trigger-alert")
def trigger_manual_alert(request: ManualWeatherTriggerRequest, db: Session = Depends(get_db)):
    """
    Manual weather alert trigger for demonstration purposes
    Allows selecting predefined weather scenarios to immediately trigger alerts
    """
    if request.weather_scenario not in WEATHER_SCENARIOS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scenario. Choose from: {', '.join(WEATHER_SCENARIOS.keys())}"
        )
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    scenario = WEATHER_SCENARIOS[request.weather_scenario]
    
    # Create alert with scenario data
    alert = climate_alert_service.create_alert_with_advisory(
        db=db,
        user_id=request.user_id,
        alert_type=scenario["alert_type"],
        severity=scenario["severity"],
        title=scenario["title"],
        description=scenario["description"],
        location=user.location,
        send_email=True,
        user_email=user.email,
        user_name=user.name,
        language=user.language or "en"
    )
    
    return {
        "message": "Alert triggered successfully",
        "alert": {
            "id": alert.id,
            "title": alert.title,
            "severity": alert.severity.value,
            "type": alert.alert_type,
            "recommendations": alert.recommendations
        }
    }

@router.get("/demo/scenarios")
def get_weather_scenarios():
    """Get list of available weather scenarios for manual triggering"""
    return {
        "scenarios": [
            {
                "key": key,
                "name": value["alert_type"],
                "description": value["description"],
                "severity": value["severity"]
            }
            for key, value in WEATHER_SCENARIOS.items()
        ]
    }

@router.get("/alerts/{user_id}")
def get_alerts(user_id: int, db: Session = Depends(get_db)):
    """Get all alerts for a user (alias for compatibility)"""
    return get_user_alerts(user_id, False, 10, db)

@router.get("/alerts/user/{user_id}")
def get_user_alerts(user_id: int, unread_only: bool = False, limit: int = 10, db: Session = Depends(get_db)):
    """Get alerts for a user"""
    alerts = climate_alert_service.get_user_alerts(
        db=db,
        user_id=user_id,
        unread_only=unread_only,
        limit=limit
    )
    
    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "title": alert.title,
            "message": alert.description,  # Add message field for frontend compatibility
            "description": alert.description,
            "recommendations": alert.recommendations,
            "created_at": alert.created_at.isoformat(),
            "is_read": alert.is_read
        }
        for alert in alerts
    ]

@router.put("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark alert as read"""
    climate_alert_service.mark_alert_read(db, alert_id)
    return {"message": "Alert marked as read"}
