import random
import string
from datetime import datetime, timedelta
from typing import Dict

# Optional import
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    print("[OTP] Twilio not installed - SMS OTP will use mock mode")

from config import get_settings
from services.email_service import email_service

settings = get_settings()

# In-memory OTP storage (use Redis in production)
otp_storage: Dict[str, Dict] = {}

class OTPService:
    def __init__(self):
        self.twilio_client = None
        if Client and settings.twilio_account_sid and settings.twilio_auth_token:
            self.twilio_client = Client(
                settings.twilio_account_sid,
                settings.twilio_auth_token
            )
        self.twilio_number = settings.twilio_phone_number
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def store_otp(self, identifier: str, otp: str, expires_in_minutes: int = 10):
        """Store OTP with expiration"""
        otp_storage[identifier] = {
            "otp": otp,
            "expires_at": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "attempts": 0
        }
    
    def verify_otp(self, identifier: str, otp: str, max_attempts: int = 3) -> bool:
        """Verify OTP"""
        if identifier not in otp_storage:
            return False
        
        stored_data = otp_storage[identifier]
        
        # Check expiration
        if datetime.utcnow() > stored_data["expires_at"]:
            del otp_storage[identifier]
            return False
        
        # Check attempts
        if stored_data["attempts"] >= max_attempts:
            del otp_storage[identifier]
            return False
        
        # Verify OTP
        if stored_data["otp"] == otp:
            del otp_storage[identifier]
            return True
        else:
            otp_storage[identifier]["attempts"] += 1
            return False
    
    def send_email_otp(self, email: str, name: str = "Farmer") -> dict:
        """Send OTP via email"""
        otp = self.generate_otp()
        self.store_otp(f"email:{email}", otp)
        
        result = email_service.send_otp_email(email, otp, name)
        return {
            "status": "sent",
            "method": "email",
            "result": result
        }
    
    def send_sms_otp(self, phone: str) -> dict:
        """Send OTP via SMS"""
        otp = self.generate_otp()
        self.store_otp(f"phone:{phone}", otp)
        
        if not self.twilio_client:
            print(f"[SMS MOCK] Sending OTP {otp} to {phone}")
            return {
                "status": "mock",
                "method": "sms",
                "message": f"SMS service not configured. OTP: {otp}"
            }
        
        try:
            message = self.twilio_client.messages.create(
                body=f"Your Smart Crop Advisory OTP is: {otp}. Valid for 10 minutes.",
                from_=self.twilio_number,
                to=phone
            )
            return {
                "status": "sent",
                "method": "sms",
                "sid": message.sid
            }
        except Exception as e:
            print(f"SMS sending error: {e}")
            return {
                "status": "error",
                "method": "sms",
                "message": str(e)
            }
    
    def verify_email_otp(self, email: str, otp: str) -> bool:
        """Verify email OTP"""
        return self.verify_otp(f"email:{email}", otp)
    
    def verify_phone_otp(self, phone: str, otp: str) -> bool:
        """Verify phone OTP"""
        return self.verify_otp(f"phone:{phone}", otp)

otp_service = OTPService()
