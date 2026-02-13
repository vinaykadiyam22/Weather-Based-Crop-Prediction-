from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class CropStatus(str, enum.Enum):
    PLANNED = "planned"
    PLANTED = "planted"
    GROWING = "growing"
    HARVESTED = "harvested"
    FAILED = "failed"

class CropHistory(Base):
    __tablename__ = "crop_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Crop details
    crop_name = Column(String(100), nullable=False)
    crop_local_name = Column(String(100))
    season = Column(String(50))  # Kharif, Rabi, Summer
    
    # Dates
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    actual_harvest_date = Column(Date, nullable=True)
    
    # Yield information
    field_size = Column(Float, nullable=True)  # in hectares
    yield_amount = Column(Float, nullable=True)  # in quintals
    yield_per_hectare = Column(Float, nullable=True)
    
    # Status tracking
    status = Column(Enum(CropStatus), default=CropStatus.PLANNED)
    
    # Context data
    soil_analysis_id = Column(Integer, ForeignKey("soil_analysis_history.id"), nullable=True)
    notes = Column(String(500), nullable=True)  # User notes about this crop
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="crop_history")
    soil_analysis = relationship("SoilAnalysisHistory", back_populates="crop_recommendations")
    
    def __repr__(self):
        return f"<CropHistory(id={self.id}, crop={self.crop_name}, season={self.season}, status={self.status})>"
