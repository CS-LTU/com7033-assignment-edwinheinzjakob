# Windows Setup Guide - Stroke Prediction System

## Prerequisites Installation

### Step 1: Install Python 3.11+

1. **Download Python**:
   - Go to https://www.python.org/downloads/
   - Download Python 3.11 or higher (Windows installer)
   - **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```powershell
   python --version
   ```
   Should show: `Python 3.11.x` or higher

3. **Verify pip**:
   ```powershell
   pip --version
   ```

### Step 2: Install MongoDB

1. **Download MongoDB Community Edition**:
   - Go to https://www.mongodb.com/try/download/community
   - Select:
     - Version: Latest (7.0+)
     - Platform: Windows
     - Package: MSI

2. **Install MongoDB**:
   - Run the installer
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service"
   - Check "Run service as Network Service user"
   - Check "Install MongoDB Compass" (optional GUI tool)

3. **Verify MongoDB Installation**:
   ```powershell
   # Check if MongoDB service is running
   Get-Service MongoDB
   
   # Should show "Running" status
   ```

4. **Start MongoDB** (if not running):
   ```powershell
   # Start MongoDB service
   net start MongoDB
   ```

5. **Test MongoDB Connection**:
   ```powershell
   # Connect to MongoDB
   mongosh
   ```
   If connection successful, type `exit` to leave.

## Project Setup

### Step 3: Navigate to Project Directory

```powershell
cd "C:\Users\SaifWaheed\Downloads\Haris Waheed\imran Python Flask\com7033-assignment"
```

### Step 4: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` prefix in your terminal.

### Step 5: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install all packages. It may take a few minutes.

### Step 6: Configure Environment Variables

1. **Create `.env` file** in the project root:
   ```powershell
   # Create .env file
   New-Item -Path .env -ItemType File
   ```

2. **Open `.env` file** and add:
   ```env
   # Flask Configuration
   FLASK_ENV=development
   FLASK_APP=run.py
   SECRET_KEY=your-secret-key-change-this-in-production

   # Database Configuration
   SQLITE_DB=users.db
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=stroke_prediction_db

   # Security Configuration (Optional - generate keys)
   # Generate encryption key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   # ENCRYPTION_KEY=your-encryption-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-change-this

   # Optional: Monitoring
   # SENTRY_DSN=your-sentry-dsn-here
   ```

3. **Generate Secret Keys** (optional but recommended):
   ```powershell
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Generate ENCRYPTION_KEY
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

### Step 7: Initialize Databases

The SQLite database will be created automatically when you first run the app.

**MongoDB** should already be running from Step 2.

### Step 8: Import Sample Data (Optional)

If you have the CSV file in `data/healthcare-dataset-stroke-data.csv`:

```powershell
python import_csv_data.py data\healthcare-dataset-stroke-data.csv
```

## Running the Application

### Step 9: Start the Application

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the application
python run.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 10: Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## First-Time Setup

1. **Register a User**:
   - Click "Register" or go to `http://localhost:5000/auth/register`
   - Fill in:
     - Username: (3-20 chars, alphanumeric + underscore)
     - Email: (valid email format)
     - Password: (min 8 chars, must include uppercase, lowercase, number, special char)
   - Click "Register"

2. **Login**:
   - Go to `http://localhost:5000/auth/login`
   - Enter your username and password
   - Click "Login"

3. **Access Dashboard**:
   - After login, you'll be redirected to the dashboard
   - View statistics and manage patients

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "MongoDB connection failed"

**Solution**: 
1. Check if MongoDB service is running:
   ```powershell
   Get-Service MongoDB
   ```

2. Start MongoDB if not running:
   ```powershell
   net start MongoDB
   ```

3. Test connection:
   ```powershell
   mongosh
   ```

### Issue: "Port 5000 already in use"

**Solution**: 
1. Find process using port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```

2. Kill the process or change port in `run.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
   ```

### Issue: "CSRF token missing"

**Solution**: Make sure `.env` file has `SECRET_KEY` set.

### Issue: PowerShell Execution Policy Error

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Running Tests

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_security.py -v
```

## Development Workflow

1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Make Changes** to code

3. **Run Application**:
   ```powershell
   python run.py
   ```

4. **Test Changes**:
   - Open browser to `http://localhost:5000`
   - Test functionality

5. **Run Tests**:
   ```powershell
   pytest
   ```

## Production Deployment

For production:
1. Set `FLASK_ENV=production` in `.env`
2. Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
3. Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
4. Use proper MongoDB connection string
5. Set up proper logging
6. Configure Sentry for error monitoring

## Quick Start Commands

```powershell
# Navigate to project
cd "C:\Users\SaifWaheed\Downloads\Haris Waheed\imran Python Flask\com7033-assignment"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Run application
python run.py

# Run tests
pytest

# Import data
python import_csv_data.py data\healthcare-dataset-stroke-data.csv
```

## Useful Commands

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check MongoDB status
Get-Service MongoDB

# Start MongoDB
net start MongoDB

# Stop MongoDB
net stop MongoDB

# View MongoDB logs
Get-Content "C:\Program Files\MongoDB\Server\7.0\log\mongod.log" -Tail 50
```

## Next Steps

1. ✅ Application is running
2. ✅ Register first user
3. ✅ Import sample data (optional)
4. ✅ Explore the dashboard
5. ✅ Add/edit/delete patients
6. ✅ Test API endpoints
7. ✅ Review security features

---

**Need Help?**
- Check logs in `app.log`
- Review error messages in terminal
- Check MongoDB connection
- Verify all environment variables are set

