from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False)  # climate, disease, etc.
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    recommendations = Column(Text)  # Gemini-generated advisory
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read
    
    # Relationship
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert {self.title} - {self.severity}>"
