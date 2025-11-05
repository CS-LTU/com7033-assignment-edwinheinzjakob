#!/usr/bin/env python3
"""
Script to import stroke prediction dataset CSV into MongoDB
Updated to work with new modular architecture
"""

import pandas as pd
from app.repositories.patient_repository import PatientRepository
from app.services.patient_service import PatientService
import sys
import os
from datetime import datetime

def clean_data(df):
    """Clean and prepare data for import"""
    print("Cleaning data...")
    
    # Handle missing BMI values
    df['bmi'].fillna(df['bmi'].median(), inplace=True)
    
    # Ensure correct data types
    df['id'] = df['id'].astype(int)
    df['age'] = df['age'].astype(float)
    df['hypertension'] = df['hypertension'].astype(int)
    df['heart_disease'] = df['heart_disease'].astype(int)
    df['avg_glucose_level'] = df['avg_glucose_level'].astype(float)
    df['bmi'] = df['bmi'].astype(float)
    df['stroke'] = df['stroke'].astype(int)
    
    # Standardize string values
    df['gender'] = df['gender'].str.strip()
    df['ever_married'] = df['ever_married'].str.strip()
    df['work_type'] = df['work_type'].str.strip()
    df['Residence_type'] = df['Residence_type'].str.strip()
    df['smoking_status'] = df['smoking_status'].str.strip()
    
    print(f"Data cleaned. Total records: {len(df)}")
    return df

def validate_data(df):
    """Validate data before import"""
    print("Validating data...")
    
    errors = []
    
    # Check for duplicate IDs
    duplicates = df['id'].duplicated().sum()
    if duplicates > 0:
        errors.append(f"Found {duplicates} duplicate patient IDs")
    
    # Check age range
    invalid_ages = df[(df['age'] < 0) | (df['age'] > 120)]
    if len(invalid_ages) > 0:
        errors.append(f"Found {len(invalid_ages)} records with invalid age")
    
    # Check BMI range
    invalid_bmi = df[(df['bmi'] < 0) | (df['bmi'] > 100)]
    if len(invalid_bmi) > 0:
        errors.append(f"Found {len(invalid_bmi)} records with invalid BMI")
    
    # Check glucose range
    invalid_glucose = df[(df['avg_glucose_level'] < 0) | (df['avg_glucose_level'] > 500)]
    if len(invalid_glucose) > 0:
        errors.append(f"Found {len(invalid_glucose)} records with invalid glucose level")
    
    # Check categorical values
    valid_genders = ['Male', 'Female', 'Other']
    invalid_genders = df[~df['gender'].isin(valid_genders)]
    if len(invalid_genders) > 0:
        errors.append(f"Found {len(invalid_genders)} records with invalid gender")
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("Data validation passed!")
    return True

def import_csv_to_mongodb(csv_file, mongo_uri='mongodb://localhost:27017/', 
                          db_name='stroke_prediction_db'):
    """Import CSV file to MongoDB"""
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found!")
        return False
    
    try:
        # Read CSV
        print(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} records from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Display basic statistics
        print("\nDataset Statistics:")
        print(df.describe())
        
        # Clean data
        df = clean_data(df)
        
        # Validate data
        if not validate_data(df):
            response = input("\nData validation failed. Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Import cancelled.")
                return False
        
        # Connect to MongoDB using new repository
        print(f"\nConnecting to MongoDB: {mongo_uri}")
        patient_repo = PatientRepository(uri=mongo_uri, db_name=db_name)
        patient_service = PatientService(patient_repo)
        
        # Store reference to patients collection for bulk operations
        patients_collection = patient_repo.patients
        
        # Check if collection already has data
        existing_count = patient_repo.count_patients()
        if existing_count > 0:
            print(f"\nWarning: Collection already contains {existing_count} records!")
            response = input("Do you want to clear existing data? (yes/no): ")
            if response.lower() == 'yes':
                print("Clearing existing data...")
                # Clear all patients using MongoDB directly
                patient_repo.patients.delete_many({})
                print("Existing data cleared.")
        
        # Convert to list of dictionaries
        records = df.to_dict('records')
        
        # Import data using service
        print(f"\nImporting {len(records)} records to MongoDB...")
        success, message, count = patient_service.import_patients(records, 'system_import')
        
        if success:
            print(f"\nImport completed successfully!")
            print(f"Total records imported: {count}")
            print(f"Message: {message}")
            
            # Display statistics
            stats = patient_service.get_statistics()
            print("\nDatabase Statistics:")
            print(f"  Total patients: {stats.get('total_patients', 0)}")
            print(f"  Stroke patients: {stats.get('stroke_patients', 0)}")
            print(f"  Male patients: {stats.get('male_count', 0)}")
            print(f"  Female patients: {stats.get('female_count', 0)}")
            print(f"  Average age: {stats.get('average_age', 0)}")
            
            patient_repo.close()
            return True
        else:
            print(f"\nImport failed: {message}")
            patient_repo.close()
            return False
        
    except Exception as e:
        print(f"Error importing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Stroke Prediction Dataset Import Tool")
    print("=" * 60)
    
    # Get CSV file path
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("Enter CSV file path: ").strip()
    
    # Get MongoDB URI (optional)
    if len(sys.argv) > 2:
        mongo_uri = sys.argv[2]
    else:
        mongo_uri = 'mongodb://localhost:27017/'
    
    # Get database name (optional)
    if len(sys.argv) > 3:
        db_name = sys.argv[3]
    else:
        db_name = 'stroke_prediction_db'
    
    # Import data
    success = import_csv_to_mongodb(csv_file, mongo_uri, db_name)
    
    if success:
        print("\n✓ Data import completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Data import failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()