"""
Database Initialization Script for Smart Crop Advisory System

This script initializes all database tables including new models:
- SoilAnalysisHistory
- CropHistory  
- CurrentCrop
- Updated User model

Run this after installing backend dependencies.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Base, engine, init_db
    from models.user import User
    from models.alert import Alert
    from models.market_price import MarketPrice
    from models.soil_analysis_history import SoilAnalysisHistory
    from models.crop_history import CropHistory
    from models.current_crop import CurrentCrop
    
    print("=" * 60)
    print("Smart Crop Advisory System - Database Initialization")
    print("=" * 60)
    print()
    
    print("📦 Importing models...")
    print("  ✓ User")
    print("  ✓ Alert")
    print("  ✓ MarketPrice")
    print("  ✓ SoilAnalysisHistory (NEW)")
    print("  ✓ CropHistory (NEW)")
    print("  ✓ CurrentCrop (NEW)")
    print()
    
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ All tables created successfully")
    print()
    
    print("📊 Database Schema:")
    print("  • users (with farming profile)")
    print("  • alerts")
    print("  • market_prices")
    print("  • soil_analysis_history")
    print("  • crop_history")
    print("  • current_crops")
    print()
    
    print("=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run backend: python app.py")
    print("  2. Run frontend: cd ../frontend && npm run dev")
    print("  3. Open: http://localhost:5173")
    print()
    
except ImportError as e:
    print()
    print("❌ Error: Missing dependencies")
    print(f"   {str(e)}")
    print()
    print("Please install required packages:")
    print("  pip install sqlalchemy fastapi uvicorn pydantic")
    print("  pip install python-multipart google-generativeai")
    print()
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"❌ Error: {str(e)}")
    print()
    sys.exit(1)
