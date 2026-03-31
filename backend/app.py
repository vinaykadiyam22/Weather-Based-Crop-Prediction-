from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from config import get_settings

# Import routes
from routes import auth, disease_detection, soil_analysis, crop_recommendation, weather, market_prices
from routes import map_intelligence
from routes import admin as admin_routes

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Smart Crop Advisory System",
    description="AI-powered agricultural decision support system for Indian farmers",
    version="1.0.0"
)

# CORS middleware - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.frontend_url
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()
    print("\n" + "="*60)
    print("[OK] Database initialized")
    print("[OK] Backend API: http://localhost:8000")
    print("[DOCS] API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")

# Include routers
app.include_router(auth.router)
app.include_router(disease_detection.router)
app.include_router(soil_analysis.router)
app.include_router(crop_recommendation.router)
app.include_router(weather.router)
app.include_router(market_prices.router)
app.include_router(map_intelligence.router)
app.include_router(admin_routes.router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Smart Crop Advisory System API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable for Render (default to 8000 for local)
    port = int(os.environ.get("PORT", 8000))
    
    print("\n[START] Smart Crop Advisory System Backend...")
    print(f"[BACKEND] http://0.0.0.0:{port}")
    print(f"[DOCS] http://0.0.0.0:{port}/docs")
    
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
