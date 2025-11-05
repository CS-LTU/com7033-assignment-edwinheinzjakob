# Quick Run Instructions - Windows

## ✅ Setup Complete!

Your environment is ready. Here's how to run the application:

## Running the Application

### Method 1: Using Python directly

1. **Activate virtual environment** (if not already active):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the application**:
   ```powershell
   python run.py
   ```

3. **Open your browser**:
   ```
   http://localhost:5000
   ```

### Method 2: Using QUICK_START.bat

Simply double-click `QUICK_START.bat` or run:
```powershell
.\QUICK_START.bat
```

## First Steps

1. **Register a User**:
   - Go to: http://localhost:5000/auth/register
   - Fill in:
     - Username: (3-20 chars, letters/numbers/underscore only)
     - Email: (valid email format)
     - Password: (min 8 chars, must include uppercase, lowercase, number, special char)
   - Click "Register"

2. **Login**:
   - Go to: http://localhost:5000/auth/login
   - Enter your credentials
   - Click "Login"

3. **Access Dashboard**:
   - After login, you'll see the dashboard
   - View statistics and manage patients

## Import Sample Data (Optional)

If you have the CSV file:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Import data
python import_csv_data.py data\healthcare-dataset-stroke-data.csv
```

## Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

## Troubleshooting

### Application won't start
- Check if MongoDB is running: `Get-Service MongoDB`
- Check if port 5000 is available
- Check terminal for error messages

### MongoDB connection error
```powershell
# Start MongoDB
net start MongoDB

# Test connection
mongosh
```

### Port 5000 already in use
Change port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## Verification Checklist

✅ Python 3.14 installed  
✅ MongoDB installed and running  
✅ Virtual environment created  
✅ Dependencies installed  
✅ .env file created  
✅ Application runs without errors  
✅ Can access http://localhost:5000  

## Next Steps

1. ✅ Application is running
2. ✅ Register first user
3. ✅ Import sample data (optional)
4. ✅ Explore the dashboard
5. ✅ Add/edit/delete patients
6. ✅ Test API endpoints
7. ✅ Review security features

---

**You're all set! The application should be running at http://localhost:5000**

