@echo off
setlocal

cd /d "%~dp0"

echo ==========================================
echo   Flavour Fleet - Launch Script
echo ==========================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check for MongoDB
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [WARNING] MongoDB does not seem to be running.
    echo Please make sure MongoDB is started.
) else (
    echo [OK] MongoDB is running.
)

REM Setup Virtual Environment if missing
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    echo [INFO] Installing dependencies...
    .venv\Scripts\python -m pip install -r backend/requirements.txt
)

echo.
echo Starting Backend Server...
start "Flavour Fleet Backend" cmd /k ".venv\Scripts\python backend/app.py"

echo.
echo Opening Website...
timeout /t 3 >nul
start http://localhost:5000

echo.
echo Application launched! The backend is running in a separate window.
echo You can close this window, but keep the backend window open.
pause
