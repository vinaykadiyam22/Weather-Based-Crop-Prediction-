# Smart Crop Advisory System - PowerShell Startup Script
# This script handles all setup and runs both backend and frontend

Write-Host "============================================================" -ForegroundColor Green
Write-Host "Smart Crop Advisory System - Automatic Startup" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

$projectRoot = $PSScriptRoot

# ============================================================
# BACKEND SETUP AND START
# ============================================================
Write-Host "[1/4] Setting up Backend..." -ForegroundColor Cyan
Set-Location "$projectRoot\backend"

# Check if virtual environment exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Install/Update Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --quiet --upgrade pip 2>$null
pip install --quiet -r requirements.txt 2>$null
pip install --quiet pydantic-settings email-validator 2>$null

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python init_database.py

# Start backend server in new window
Write-Host "Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; .\venv\Scripts\Activate.ps1; python app.py"

Set-Location $projectRoot

# ============================================================
# FRONTEND SETUP AND START
# ============================================================
Write-Host ""
Write-Host "[2/4] Setting up Frontend..." -ForegroundColor Cyan
Set-Location "$projectRoot\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "Node dependencies already installed (skipping)" -ForegroundColor Gray
}

# Start frontend server in new window
Write-Host "Starting Frontend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; npm run dev"

Set-Location $projectRoot

# ============================================================
# COMPLETION
# ============================================================
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✅ Smart Crop Advisory System Started Successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Yellow
Write-Host "Close those windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening application in browser..." -ForegroundColor Green

# Wait a bit for servers to start
Start-Sleep -Seconds 5

# Open application in default browser
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
