@echo off
REM Simple script to stop all running servers

echo Stopping Smart Crop Advisory System...
echo.

echo Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [OK] All servers stopped!
echo.
pause
