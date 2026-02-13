from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class SoilAnalysisHistory(Base):
    __tablename__ = "soil_analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Manual soil type input
    soil_type = Column(String(50), nullable=True)
    
    # NPK and pH parameters
    nitrogen = Column(Float, nullable=False)
    phosphorus = Column(Float, nullable=False)
    potassium = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    organic_matter = Column(Float, nullable=True)
    
    # Analysis results
    soil_health = Column(String(20))  # good, medium, poor
    fertilizer_recommendations = Column(JSON)  # List of fertilizer names
    gemini_advisory = Column(Text)  # AI-generated interpretation
    
    # Metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    location = Column(String(200))  # Where sample was taken
    
    # Relationships
    user = relationship("User", back_populates="soil_analyses")
    crop_recommendations = relationship("CropHistory", back_populates="soil_analysis")
    
    def __repr__(self):
        return f"<SoilAnalysis(id={self.id}, user_id={self.user_id}, date={self.analysis_date})>"
