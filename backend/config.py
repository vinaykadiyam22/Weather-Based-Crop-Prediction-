from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load .env from project root (parent of backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./crop_advisory.db"
    
    # API Keys
    gemini_api_key: str = ""
    openweather_api_key: str = ""
    sendgrid_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    google_translate_api_key: str = ""
    data_gov_in_api_key: str = ""  # For market prices (data.gov.in)
    
    # Email
    from_email: str = "noreply@cropadvisory.com"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days
    
    # URLs
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    
    class Config:
        env_file = _env_path
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
