from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database (import models first)
def init_db():
    from models.user import User
    from models.alert import Alert
    from models.market_price import MarketPrice
    from models.soil_analysis_history import SoilAnalysisHistory
    from models.crop_history import CropHistory
    from models.current_crop import CurrentCrop
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
