@echo off
REM Quick CSV Import Script
echo ========================================
echo CSV Data Import Tool
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if CSV file path provided
if "%1"=="" (
    echo Usage: QUICK_IMPORT.bat "path\to\file.csv"
    echo.
    echo Example:
    echo   QUICK_IMPORT.bat "data\healthcare-dataset-stroke-data.csv"
    echo.
    echo Or use default file:
    set CSV_FILE=data\healthcare-dataset-stroke-data.csv
) else (
    set CSV_FILE=%1
)

REM Check if file exists
if not exist "%CSV_FILE%" (
    echo ERROR: File not found: %CSV_FILE%
    pause
    exit /b 1
)

echo Importing: %CSV_FILE%
echo.

REM Run import
python import_csv_data.py "%CSV_FILE%"

echo.
pause

