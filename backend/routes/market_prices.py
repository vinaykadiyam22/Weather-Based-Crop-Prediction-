from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.market_price import MarketPrice
from services.market_price_service import (
    get_season_prices_for_location,
    get_crop_prices_for_location,
    get_current_season,
    get_season_crops_for_location,
)
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api/market", tags=["Market Prices"])


class SeasonPricesRequest(BaseModel):
    location: str


@router.post("/season-prices")
def get_season_prices(request: SeasonPricesRequest):
    """Get market prices for current season crops in user's location."""
    return get_season_prices_for_location(request.location)


@router.get("/season")
def get_season_info():
    """Get current crop season."""
    return {"season": get_current_season()}


@router.get("/prices/{crop_name}")
def get_crop_prices(
    crop_name: str,
    state: str = None,
    location: str = None,
    days: int = 30,
    db: Session = Depends(get_db),
):
    """
    Get market prices for a specific crop.
    If location is provided, uses live/fallback data; otherwise uses DB.
    """
    if location:
        return get_crop_prices_for_location(crop_name, location, days)

    # Fallback to DB
    query = db.query(MarketPrice).filter(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    if state:
        query = query.filter(MarketPrice.state == state)
    start_date = datetime.now().date() - timedelta(days=days)
    query = query.filter(MarketPrice.date >= start_date)
    prices = query.order_by(MarketPrice.date.desc()).all()

    if len(prices) >= 2:
        latest_price = prices[0].price
        older_price = prices[-1].price
        trend = "up" if latest_price > older_price else "down" if latest_price < older_price else "stable"
        change_percent = ((latest_price - older_price) / older_price * 100) if older_price > 0 else 0
    else:
        trend = "stable"
        change_percent = 0

    return {
        "crop_name": crop_name,
        "prices": [
            {"state": p.state, "market": p.market, "price": p.price, "date": p.date.isoformat()}
            for p in prices
        ],
        "count": len(prices),
        "trend": trend,
        "change_percent": round(change_percent, 2),
        "latest_price": prices[0].price if prices else None,
    }


@router.get("/states")
def get_states(db: Session = Depends(get_db)):
    """Get list of states with price data (from DB or default list)."""
    states = db.query(MarketPrice.state).distinct().all()
    if states:
        return {"states": [s[0] for s in states]}
    return {
        "states": [
            "Punjab", "Haryana", "Maharashtra", "Gujarat", "Andhra Pradesh",
            "Karnataka", "Tamil Nadu", "West Bengal", "Uttar Pradesh", "Madhya Pradesh",
        ]
    }


@router.post("/seed-mock-data")
def seed_mock_data(db: Session = Depends(get_db)):
    """Seed database with mock market price data (legacy)."""
    import random

    crops = ["Rice", "Wheat", "Cotton", "Groundnut", "Sugarcane", "Maize", "Tomato", "Onion", "Potato"]
    states = ["Punjab", "Haryana", "Maharashtra", "Gujarat", "Andhra Pradesh", "Karnataka", "Tamil Nadu"]
    markets = ["APMC Market", "Mandi", "Local Market"]

    db.query(MarketPrice).delete()
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        for crop in crops:
            for state in random.sample(states, 2):
                base_price = random.uniform(1000, 5000)
                price = MarketPrice(
                    crop_name=crop,
                    state=state,
                    market=random.choice(markets),
                    price=round(base_price + random.uniform(-200, 200), 2),
                    date=date,
                )
                db.add(price)
    db.commit()
    count = db.query(MarketPrice).count()
    return {"message": f"Seeded {count} market price records"}
