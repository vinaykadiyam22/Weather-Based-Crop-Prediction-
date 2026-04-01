from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from config import get_settings
import os

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

# CORS middleware - Allow all origins (frontend served from same origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Include all API routers
app.include_router(auth.router)
app.include_router(disease_detection.router)
app.include_router(soil_analysis.router)
app.include_router(crop_recommendation.router)
app.include_router(weather.router)
app.include_router(market_prices.router)
app.include_router(map_intelligence.router)
app.include_router(admin_routes.router)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API info endpoint
@app.get("/api")
def api_info():
    return {
        "message": "Smart Crop Advisory System API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

# ─── Serve React Frontend Static Files ───────────────────────────────────────
# Path: when running from backend/ dir, frontend/dist is one level up
FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "frontend",
    "dist"
)

if os.path.exists(FRONTEND_DIST):
    print(f"[FRONTEND] Serving React app from: {FRONTEND_DIST}")

    # Mount static assets (JS, CSS, images)
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/")
    async def serve_root():
        """Serve the React app root"""
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Catch-all: serve React app for all non-API routes (SPA routing)"""
        # Check if the file exists in dist (e.g. favicon.ico, manifest.json)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # For all other routes, return index.html (React Router handles it)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

else:
    print(f"[WARNING] Frontend dist not found at: {FRONTEND_DIST}")
    print("[INFO] Running backend-only mode. Build frontend to enable full-stack serving.")

    @app.get("/")
    def root():
        return {
            "message": "Smart Crop Advisory System API",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build' in the frontend directory."
        }

if __name__ == "__main__":
    import uvicorn

    # Get port from environment variable for Render (default to 8000 for local)
    port = int(os.environ.get("PORT", 8000))

    print("\n[START] Smart Crop Advisory System Backend...")
    print(f"[BACKEND] http://0.0.0.0:{port}")
    print(f"[DOCS] http://0.0.0.0:{port}/docs")

    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
