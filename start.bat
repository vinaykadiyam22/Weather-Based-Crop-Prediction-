@echo off
REM ============================================================
REM Smart Crop Advisory System - One-Click Startup
REM Double-click this file to start everything!
REM ============================================================

TITLE Smart Crop Advisory System

echo.
echo ============================================================
echo    SMART CROP ADVISORY SYSTEM
echo ============================================================
echo.
echo Starting servers...
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM ============================================================
REM STEP 1: Clean up old servers
REM ============================================================
echo [1/3] Stopping old servers...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done!
echo.

REM ============================================================
REM STEP 2: Start Backend Server (with CORS enabled)
REM ============================================================
echo [2/3] Starting Backend...
cd backend
start "BACKEND - http://localhost:8000" cmd /k "title BACKEND SERVER && color 0B && echo. && echo Backend Server Running && echo URL: http://localhost:8000 && echo API Docs: http://localhost:8000/docs && echo. && echo KEEP THIS WINDOW OPEN! && echo. && python app.py"
cd ..
echo       Backend starting in blue window...
timeout /t 4 /nobreak >nul
echo.

REM ============================================================
REM STEP 3: Start Frontend Server
REM ============================================================
echo [3/3] Starting Frontend...
cd frontend
start "FRONTEND - http://localhost:5173" cmd /k "title FRONTEND SERVER && color 0E && echo. && echo Frontend Server Running && echo URL: http://localhost:5173 && echo. && echo KEEP THIS WINDOW OPEN! && echo. && npm run dev"
cd ..
echo       Frontend starting in yellow window...
echo.

REM ============================================================
REM Wait for servers to fully start
REM ============================================================
echo ============================================================
echo    Please wait while servers start...
echo ============================================================
echo.
timeout /t 8 /nobreak

REM ============================================================
REM Open Browser
REM ============================================================
echo Opening browser...
start http://localhost:5173
echo.

REM ============================================================
REM Success Message
REM ============================================================
echo ============================================================
echo    SUCCESS! Application is Running
echo ============================================================
echo.
echo   Two windows have opened:
echo   - BLUE WINDOW   = Backend Server
echo   - YELLOW WINDOW = Frontend Server
echo.
echo   URLs:
echo   - Main App:  http://localhost:5173
echo   - API Docs:  http://localhost:8000/docs
echo.
echo   IMPORTANT:
echo   - Keep both colored windows open!
echo   - Close them when you want to stop the servers
echo.
echo   Your browser should now be open.
echo   If you see CORS errors, the backend may still be starting.
echo   Wait 5 seconds and refresh the page.
echo.
echo ============================================================
echo.
echo Press any key to close this startup window...
pause >nul
