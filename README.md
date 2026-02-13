# Smart Crop Advisory System

AI-powered agricultural decision support system for Indian farmers.

---

## Quick Start

**Double-click `start.bat`** to start the application. It will:
1. Stop any existing servers
2. Start backend (blue window)
3. Start frontend (yellow window)
4. Open your browser automatically

**URLs:**
- **Application:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

**To stop:** Close the blue (backend) and yellow (frontend) windows, or run `stop.bat`.

---

## Manual Start

If the batch file does not work:

**Terminal 1 - Backend:**
```cmd
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm install
npm run dev
```

Then open: http://localhost:5173

---

## System Requirements

- **Python:** 3.8 or higher
- **Node.js:** 16 or higher

---

## Features (Full Checklist)

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| 1 | **Home / Landing** | ✅ | Hero image, Login, Register, About links |
| 2 | **Authentication** | ✅ | Email + OTP, SMS OTP; Registration (name, email, phone, location) |
| 3 | **About Page** | ✅ | Purpose, how it helps farmers, technologies, support commitment |
| 4 | **Dashboard** | ✅ | Background image, quick access to all modules |
| 5 | **Soil Analysis** | ✅ | NPK, pH, fertilizer recommendations, soil health |
| 6 | **Crop Recommendation** | ✅ | Soil, weather, market, climate—multi-factor analysis |
| 7 | **Weather** | ✅ | Open-Meteo API: current, forecast, rainfall, humidity |
| 8 | **Market Prices** | ✅ | Live mandi prices, trends, sell/hold suggestions |
| 9 | **Pest & Disease Detection** | ✅ | Image upload, ML model, remedies, prevention |
| 10 | **Soil Type Detection** | ✅ | Manual selection OR image upload |
| 11 | **Multilingual** | ✅ | Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati |
| 12 | **Voice / Text Reader** | 🔜 | Future scope |

**Dataset notes:** Disease detection uses PlantVillage (38 classes, ~87k training images). Crop data: `crops.json`. Soil: rule-based logic. Market: data.gov.in or fallback. For production scale, consider expanding soil/crop datasets to 10k+ records as per requirements.

---

## Project Structure

```
backend/          # FastAPI server, SQLite database
frontend/         # React + Vite frontend
start.bat         # One-click startup
stop.bat          # Stop all servers
```

---

## Configuration

Copy `.env.example` to `.env` and add your API keys:

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Required for AI advisory generation |
| `OPENWEATHER_API_KEY` | Optional - real weather (uses mock if empty) |
| `SENDGRID_API_KEY` | Optional - email notifications |
| `TWILIO_*` | Optional - SMS OTP |

---

## Troubleshooting

### Batch file closes immediately
Ensure Python and Node.js are installed and in PATH:
```cmd
python --version
node --version
```

### CORS error in browser
Wait 5-10 seconds for the backend to fully start, then refresh. The backend allows origins from localhost:5173.

### Port already in use
Run `stop.bat` to stop existing servers, then try again.

### Use localhost, not 0.0.0.0
Always use `http://localhost:5173` and `http://localhost:8000` in your browser.

---

## API Optimization (Gemini)

The system includes built-in optimizations to reduce Gemini API usage:

- **Response caching:** 1-hour cache for identical requests
- **Rate limiting:** Minimum 1 second between API calls
- **Request deduplication:** Prevents simultaneous identical requests

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `start.bat` | Start backend and frontend |
| `stop.bat` | Stop all servers |
| `diagnose.bat` | Check Python, Node, ports, and project structure |
| `start-debug.bat` | Start with full diagnostic checks |
