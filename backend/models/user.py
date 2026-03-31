from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    location = Column(String(200), nullable=False)
    language = Column(String(10), default="en")  # Language preference
    hashed_password = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Farming profile
    farm_size = Column(Float, nullable=True)  # in hectares
    farming_experience = Column(Integer, nullable=True)  # years
    preferred_crops = Column(JSON, nullable=True)  # List of crop names
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    soil_analyses = relationship("SoilAnalysisHistory", back_populates="user", cascade="all, delete-orphan")
    crop_history = relationship("CropHistory", back_populates="user", cascade="all, delete-orphan")
    current_crops = relationship("CurrentCrop", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
