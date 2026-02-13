from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class CurrentCrop(Base):
    __tablename__ = "current_crops"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Crop details
    crop_name = Column(String(100), nullable=False)
    crop_local_name = Column(String(100))
    
    # Planting information
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    field_size = Column(Float, nullable=True)  # in hectares
    field_location = Column(String(200))  # Specific field location/name
    
    # Health monitoring
    health_status = Column(String(50), default="healthy")  # healthy, at_risk, diseased
    last_disease_check = Column(DateTime, nullable=True)
    disease_detected = Column(String(200), nullable=True)
    
    # Watering and care
    last_watered = Column(Date, nullable=True)
    last_fertilized = Column(Date, nullable=True)
    
    # Notes
    notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="current_crops")
    
    def __repr__(self):
        return f"<CurrentCrop(id={self.id}, crop={self.crop_name}, health={self.health_status})>"
