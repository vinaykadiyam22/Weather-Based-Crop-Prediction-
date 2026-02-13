@echo off
REM DEBUG VERSION - This will show all errors and not close
REM Use this to see what's happening

title Smart Crop Advisory - Debug Mode
color 0C

echo.
echo ============================================================
echo    DEBUG MODE - Checking what's happening...
echo ============================================================
echo.

REM Navigate to project root
cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM ============================================================
REM CHECK PYTHON
REM ============================================================
echo [CHECK 1] Testing Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Make sure Python is installed and added to PATH
    pause
    exit /b 1
)
echo Python: OK
echo.

REM ============================================================
REM CHECK NODE
REM ============================================================
echo [CHECK 2] Testing Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found!
    echo Make sure Node.js is installed and added to PATH
    pause
    exit /b 1
)
echo Node.js: OK
echo.

REM ============================================================
REM CHECK PROJECT STRUCTURE
REM ============================================================
echo [CHECK 3] Checking project structure...

if not exist "backend\" (
    echo ERROR: backend folder not found!
    echo Make sure you're running this from the project root
    pause
    exit /b 1
)
echo Backend folder: OK

if not exist "frontend\" (
    echo ERROR: frontend folder not found!
    echo Make sure you're running this from the project root
    pause
    exit /b 1
)
echo Frontend folder: OK

if not exist "backend\app.py" (
    echo ERROR: backend\app.py not found!
    pause
    exit /b 1
)
echo Backend app.py: OK

if not exist "frontend\package.json" (
    echo ERROR: frontend\package.json not found!
    pause
    exit /b 1
)
echo Frontend package.json: OK
echo.

REM ============================================================
REM CHECK BACKEND DEPENDENCIES
REM ============================================================
echo [CHECK 4] Checking backend setup...
cd backend

echo Testing database initialization...
python init_database.py
if %errorlevel% neq 0 (
    echo ERROR: Database initialization failed!
    echo Check the errors above
    cd ..
    pause
    exit /b 1
)
echo Database: OK
cd ..
echo.

REM ============================================================
REM CHECK FRONTEND DEPENDENCIES
REM ============================================================
echo [CHECK 5] Checking frontend setup...
cd frontend

if not exist "node_modules\" (
    echo Node modules not found. Installing...
    echo This may take 2-5 minutes...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed!
        cd ..
        pause
        exit /b 1
    )
)
echo Frontend dependencies: OK
cd ..
echo.

REM ============================================================
REM ALL CHECKS PASSED
REM ============================================================
echo ============================================================
echo    ALL CHECKS PASSED!
echo ============================================================
echo.
echo Your system is ready to run the application.
echo.
echo Now let's try starting the servers...
echo.
pause

REM ============================================================
REM START BACKEND
REM ============================================================
echo.
echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "title Backend && color 0B && python app.py"
cd ..
echo Backend started in new window
timeout /t 3 /nobreak >nul
echo.

REM ============================================================
REM START FRONTEND
REM ============================================================
echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "title Frontend && color 0E && npm run dev"
cd ..
echo Frontend started in new window
timeout /t 3 /nobreak >nul
echo.

REM ============================================================
REM DONE
REM ============================================================
echo ============================================================
echo    SERVERS STARTED!
echo ============================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Two windows have opened - keep them open!
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start http://localhost:5173

echo.
echo Done! Press any key to close this debug window...
pause >nul
