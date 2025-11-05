@echo off
REM Quick Start Script for Windows
echo ========================================
echo Stroke Prediction System - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed!
    echo.
) else (
    echo Dependencies already installed.
    echo.
)

REM Check MongoDB
echo Checking MongoDB...
net start MongoDB >nul 2>&1
if errorlevel 1 (
    echo MongoDB service is not running. Attempting to start...
    net start MongoDB
    if errorlevel 1 (
        echo WARNING: Could not start MongoDB. Please start it manually.
        echo.
    )
) else (
    echo MongoDB is running.
    echo.
)

REM Check .env file
if not exist ".env" (
    echo .env file not found. Creating default .env file...
    (
        echo FLASK_ENV=development
        echo FLASK_APP=run.py
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo SQLITE_DB=users.db
        echo MONGO_URI=mongodb://localhost:27017/
        echo MONGO_DB_NAME=stroke_prediction_db
        echo JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
    ) > .env
    echo Default .env file created!
    echo.
)

echo ========================================
echo Starting Application...
echo ========================================
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the application
python run.py

pause

