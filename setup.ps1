# PowerShell Setup Script for Stroke Prediction System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stroke Prediction System - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+ from python.org" -ForegroundColor Red
    exit 1
}

# Check MongoDB
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
$mongoService = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
if ($mongoService) {
    if ($mongoService.Status -eq 'Running') {
        Write-Host "✓ MongoDB is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ MongoDB service exists but is not running. Starting..." -ForegroundColor Yellow
        Start-Service MongoDB
        Write-Host "✓ MongoDB started" -ForegroundColor Green
    }
} else {
    Write-Host "✗ MongoDB service not found! Please install MongoDB from mongodb.com" -ForegroundColor Red
    Write-Host "  The application may still work, but MongoDB features will fail." -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
    $jwtKey = python -c "import secrets; print(secrets.token_hex(32))"
    
    @"
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=$secretKey
SQLITE_DB=users.db
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=stroke_prediction_db
JWT_SECRET_KEY=$jwtKey
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Host "✓ .env file created with generated keys" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run application: python run.py" -ForegroundColor White
Write-Host "3. Open browser: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Or run: .\QUICK_START.bat" -ForegroundColor Cyan
Write-Host ""

