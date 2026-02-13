@echo off
REM Troubleshooting script - shows what's running and helps diagnose issues

echo ============================================================
echo Smart Crop Advisory System - Diagnostic Tool
echo ============================================================
echo.

echo 1. Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo   [FAIL] Python not found in PATH
) else (
    echo   [OK] Python is installed
)
echo.

echo 2. Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo   [FAIL] Node.js not found in PATH
) else (
    echo   [OK] Node.js is installed
)
echo.

echo 3. Checking npm installation...
npm --version
if %errorlevel% neq 0 (
    echo   [FAIL] npm not found in PATH
) else (
    echo   [OK] npm is installed
)
echo.

echo 4. Checking if Backend is running (port 8000)...
netstat -ano | findstr :8000
if %errorlevel% neq 0 (
    echo   [INFO] No process running on port 8000
) else (
    echo   [OK] Backend is running
)
echo.

echo 5. Checking if Frontend is running (port 5173)...
netstat -ano | findstr :5173
if %errorlevel% neq 0 (
    echo   [INFO] No process running on port 5173
) else (
    echo   [OK] Frontend is running
)
echo.

echo 6. Checking project structure...
if exist "backend\app.py" (
    echo   [OK] Backend files found
) else (
    echo   [FAIL] Backend files missing
)

if exist "frontend\package.json" (
    echo   [OK] Frontend files found
) else (
    echo   [FAIL] Frontend files missing
)
echo.

echo 7. Checking database...
if exist "backend\crop_advisory.db" (
    echo   [OK] Database file exists
) else (
    echo   [WARN] Database file not found (will be created on first run)
)
echo.

echo 8. Checking backend dependencies...
if exist "backend\venv\" (
    echo   [OK] Virtual environment exists
) else (
    echo   [WARN] Virtual environment not found (will be created)
)
echo.

echo 9. Checking frontend dependencies...
if exist "frontend\node_modules\" (
    echo   [OK] Node modules installed
) else (
    echo   [WARN] Node modules not installed (will be installed)
)
echo.

echo ============================================================
echo Diagnostic Complete
echo ============================================================
echo.
echo If you see any [FAIL] marks above, those need to be fixed.
echo.
pause
