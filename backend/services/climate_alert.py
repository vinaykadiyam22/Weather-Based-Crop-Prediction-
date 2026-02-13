from datetime import datetime, timedelta
from typing import Optional
from services.weather_service import weather_service
from services.gemini_service import generate_climate_advisory
from services.email_service import email_service
from models.alert import Alert, AlertSeverity
from sqlalchemy.orm import Session

class ClimateAlertService:
    """Service for monitoring weather and generating climate alerts"""
    
    # Alert thresholds
    HEAVY_RAIN_THRESHOLD = 100  # mm per day
    HIGH_WIND_THRESHOLD = 40  # km/h
    EXTREME_TEMP_HIGH = 42  # °C
    EXTREME_TEMP_LOW = 5  # °C
    
    def check_weather_alerts(self, location: str, lat: float = None, lon: float = None) -> list:
        """
        Check for potential weather-related alerts
        
        Returns list of alerts
        """
        alerts = []
        
        # Get current weather
        current_weather = weather_service.get_current_weather(location, lat, lon)
        
        # Get forecast
        forecast = weather_service.get_forecast(location, lat, lon)
        
        # Check for heavy rainfall
        if forecast and 'list' in forecast:
            for day_forecast in forecast['list'][:3]:  # Check next 3 days
                rain = day_forecast.get('rain', {}).get('3h', 0)
                if rain > self.HEAVY_RAIN_THRESHOLD:
                    dt_txt = day_forecast.get('dt_txt', 'upcoming')
                    alerts.append({
                        'type': 'heavy_rainfall',
                        'severity': 'high',
                        'title': 'Heavy Rainfall Expected',
                        'description': f'Heavy rain expected ({rain}mm). Risk to crops.',
                        'date': dt_txt,
                        'expected_time': dt_txt
                    })
        
        # Check for high winds
        if current_weather and 'wind' in current_weather:
            wind_speed = current_weather['wind'].get('speed', 0) * 3.6  # m/s to km/h
            if wind_speed > self.HIGH_WIND_THRESHOLD:
                alerts.append({
                    'type': 'high_winds',
                    'severity': 'medium',
                    'title': 'High Wind Alert',
                    'description': f'Strong winds detected ({wind_speed:.1f} km/h). Secure crops.',
                    'date': 'now',
                    'expected_time': 'Current - next few hours'
                })
        
        # Check for extreme temperature
        if current_weather and 'main' in current_weather:
            temp = current_weather['main'].get('temp', 25)
            if temp > self.EXTREME_TEMP_HIGH:
                alerts.append({
                    'type': 'extreme_heat',
                    'severity': 'high',
                    'title': 'Extreme Heat Warning',
                    'description': f'Very high temperature ({temp}°C). Irrigation recommended.',
                    'date': 'now',
                    'expected_time': 'Current - next 24 hours'
                })
            elif temp < self.EXTREME_TEMP_LOW:
                alerts.append({
                    'type': 'cold_wave',
                    'severity': 'high',
                    'title': 'Cold Wave Alert',
                    'description': f'Very low temperature ({temp}°C). Frost protection needed.',
                    'date': 'now',
                    'expected_time': 'Current - next 24 hours'
                })
        
        return alerts
    
    def create_alert_with_advisory(
        self,
        db: Session,
        user_id: int,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        location: str,
        weather_data: dict = None,
        send_email: bool = True,
        user_email: str = None,
        user_name: str = "Farmer",
        expected_time: str = None,
        language: str = "en"
    ) -> Alert:
        """
        Create alert with Gemini-generated advisory and optionally send email.
        Includes expected time window and language support.
        """
        # Build description with expected time window (spec 2.2)
        full_description = description
        if expected_time:
            full_description += f"\n\nExpected time window: {expected_time}"
        
        # Generate advisory using Gemini (with language)
        advisory = generate_climate_advisory(
            event_type=alert_type,
            severity=severity,
            location=location,
            weather_data=weather_data or {},
            language=language
        )
        
        # Create alert in database
        alert = Alert(
            user_id=user_id,
            alert_type=alert_type,
            severity=AlertSeverity[severity.upper()],
            title=title,
            description=full_description,
            recommendations=advisory
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Send email notification (spec 7)
        if send_email and user_email:
            email_service.send_climate_alert(
                to_email=user_email,
                alert_title=title,
                severity=severity,
                advisory=advisory,
                name=user_name
            )
        
        return alert

    def sync_weather_alerts(
        self,
        db: Session,
        user_id: int,
        location: str,
        user_email: str = None,
        user_name: str = "Farmer",
        language: str = "en"
    ) -> dict:
        """
        Check weather for risks, create persisted alerts + send email.
        Deduplicates: avoids creating same alert type within 24h.
        """
        detected = self.check_weather_alerts(location=location)
        created = []
        current_weather = weather_service.get_current_weather(location)
        weather_data = current_weather or {}

        for d in detected:
            # Dedupe: check if similar alert exists in last 24h
            since = datetime.utcnow() - timedelta(hours=24)
            existing = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.alert_type == d.get('type', d.get('title', '')),
                Alert.created_at >= since
            ).first()
            if existing:
                continue
            
            alert_type = d.get('type', 'weather')
            severity = d.get('severity', 'medium')
            title = d.get('title', 'Weather Alert')
            description = d.get('description', '')
            expected_time = d.get('expected_time')
            
            alert = self.create_alert_with_advisory(
                db=db,
                user_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                description=description,
                location=location,
                weather_data=weather_data,
                send_email=True,
                user_email=user_email,
                user_name=user_name,
                expected_time=expected_time,
                language=language
            )
            created.append(alert.id)
        
        return {"detected": len(detected), "created": created, "alerts": detected}
    
    def get_user_alerts(
        self,
        db: Session,
        user_id: int,
        unread_only: bool = False,
        limit: int = 10
    ) -> list:
        """Get alerts for a user"""
        query = db.query(Alert).filter(Alert.user_id == user_id)
        
        if unread_only:
            query = query.filter(Alert.is_read == 0)
        
        query = query.order_by(Alert.created_at.desc()).limit(limit)
        
        return query.all()
    
    def mark_alert_read(self, db: Session, alert_id: int):
        """Mark alert as read"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_read = 1
            db.commit()

climate_alert_service = ClimateAlertService()
