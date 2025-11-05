# How to Import CSV Data

You have **3 options** to import your CSV file into the database:

## Option 1: Command Line Script (Recommended) ✅

This is the easiest and most reliable method:

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Import your CSV file
python import_csv_data.py "data\healthcare-dataset-stroke-data.csv"
```

Or if your CSV is in a different location:
```powershell
python import_csv_data.py "C:\path\to\your\file.csv"
```

**What it does:**
- Reads and validates your CSV file
- Cleans the data (handles missing values)
- Validates all fields
- Imports into MongoDB with progress updates
- Shows statistics after import

## Option 2: Web Interface 🌐

1. **Login** to your application: `http://localhost:5000/auth/login`

2. **Navigate** to Import Data:
   - Click "Patients" in the navigation
   - Click "Import" button
   - Or go directly to: `http://localhost:5000/patients/import`

3. **Upload CSV**:
   - Click "Choose File"
   - Select your CSV file
   - Click "Import Data"

**Note:** The web interface has file size limits (16MB max).

## Option 3: Using Python Script with Custom Options

```powershell
# Import with custom MongoDB URI
python import_csv_data.py "data\healthcare-dataset-stroke-data.csv" "mongodb://localhost:27017/" "stroke_prediction_db"
```

## CSV File Format Requirements

Your CSV file must have these columns (in any order):

- `id` - Unique patient identifier (integer)
- `gender` - Male, Female, or Other
- `age` - Patient age (0-120)
- `hypertension` - 0 or 1
- `heart_disease` - 0 or 1
- `ever_married` - Yes or No
- `work_type` - Children, Govt_job, Never_worked, Private, or Self-employed
- `Residence_type` - Rural or Urban
- `avg_glucose_level` - Average glucose level (0-500)
- `bmi` - Body Mass Index (0-100)
- `smoking_status` - formerly smoked, never smoked, smokes, or Unknown
- `stroke` - 0 or 1

## Example: Import Your Data

```powershell
# Activate virtual environment (if not already)
.\venv\Scripts\Activate.ps1

# Import the CSV file in data folder
python import_csv_data.py data\healthcare-dataset-stroke-data.csv
```

You should see output like:
```
============================================================
Stroke Prediction Dataset Import Tool
============================================================
Reading CSV file: data\healthcare-dataset-stroke-data.csv
Loaded 5110 records from CSV
Columns: ['id', 'gender', 'age', 'hypertension', ...]

Cleaning data...
Data cleaned. Total records: 5110

Validating data...
Data validation passed!

Connecting to MongoDB: mongodb://localhost:27017/

Importing 5110 records to MongoDB...
Imported 100/5110 records...
Imported 200/5110 records...
...
Imported 5110/5110 records...

Import completed successfully!
Total records imported: 5110

Database Statistics:
  Total patients: 5110
  Stroke patients: 249
  Male patients: 2994
  Female patients: 2115
  Average age: 43.23
```

## Troubleshooting

### "File not found" error
- Make sure the file path is correct
- Use quotes around paths with spaces
- Use forward slashes `/` or double backslashes `\\` in paths

### "Duplicate ID" error
- The script will warn about duplicate IDs
- You can choose to continue anyway or fix the CSV first

### "Validation failed" error
- Check your CSV has all required columns
- Verify data types match requirements
- Check for invalid values (e.g., age > 120, BMI > 100)

### MongoDB connection error
- Make sure MongoDB is running: `Get-Service MongoDB`
- Start MongoDB if needed: `net start MongoDB`

## Quick Import Command

```powershell
# One-line import (assuming CSV is in data folder)
python import_csv_data.py data\healthcare-dataset-stroke-data.csv
```

---

**After importing, you can view the data in the web interface at:**
- Patients list: `http://localhost:5000/patients`
- Dashboard: `http://localhost:5000/dashboard`

