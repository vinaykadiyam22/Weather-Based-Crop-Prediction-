from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from datetime import datetime
from database import Base

class MarketPrice(Base):
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    market = Column(String, nullable=False)
    price = Column(Float, nullable=False)  # Price per quintal
    unit = Column(String, default="quintal")
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketPrice {self.crop_name} - ₹{self.price}>"
