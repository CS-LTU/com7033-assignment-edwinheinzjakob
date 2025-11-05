@echo off
REM Simple batch file to start the application
echo Starting Stroke Prediction System...
echo.

REM Activate virtual environment using batch file (no PowerShell needed)
call venv\Scripts\activate.bat

REM Run the application
echo Application starting at http://localhost:5000
echo Press Ctrl+C to stop
echo.
python run.py

pause

