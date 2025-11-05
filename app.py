from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
from pymongo import MongoClient
import pandas as pd
import secrets
import re
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['stroke_prediction_db']
patients_collection = mongo_db['patients']

# SQLite Configuration for User Authentication
SQLITE_DB = 'users.db'

# Initialize SQLite Database
def init_sqlite_db():
    """Initialize SQLite database for user authentication"""
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Input Validation Functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username (alphanumeric and underscore only, 3-20 chars)"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def sanitize_input(data):
    """Sanitize user input to prevent XSS"""
    if isinstance(data, str):
        return data.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    return data

def validate_patient_data(data):
    """Validate patient data fields"""
    errors = []
    
    # Validate age
    try:
        age = float(data.get('age', 0))
        if age < 0 or age > 120:
            errors.append("Age must be between 0 and 120")
    except ValueError:
        errors.append("Age must be a valid number")
    
    # Validate gender
    if data.get('gender') not in ['Male', 'Female', 'Other']:
        errors.append("Invalid gender value")
    
    # Validate hypertension
    if data.get('hypertension') not in ['0', '1', 0, 1]:
        errors.append("Hypertension must be 0 or 1")
    
    # Validate heart_disease
    if data.get('heart_disease') not in ['0', '1', 0, 1]:
        errors.append("Heart disease must be 0 or 1")
    
    # Validate ever_married
    if data.get('ever_married') not in ['Yes', 'No']:
        errors.append("Ever married must be Yes or No")
    
    # Validate work_type
    valid_work_types = ['Children', 'Govt_job', 'Never_worked', 'Private', 'Self-employed']
    if data.get('work_type') not in valid_work_types:
        errors.append("Invalid work type")
    
    # Validate residence_type
    if data.get('Residence_type') not in ['Rural', 'Urban']:
        errors.append("Residence type must be Rural or Urban")
    
    # Validate avg_glucose_level
    try:
        glucose = float(data.get('avg_glucose_level', 0))
        if glucose < 0 or glucose > 500:
            errors.append("Average glucose level must be between 0 and 500")
    except ValueError:
        errors.append("Average glucose level must be a valid number")
    
    # Validate BMI
    try:
        bmi = float(data.get('bmi', 0))
        if bmi < 0 or bmi > 100:
            errors.append("BMI must be between 0 and 100")
    except ValueError:
        errors.append("BMI must be a valid number")
    
    # Validate smoking_status
    valid_smoking = ['formerly smoked', 'never smoked', 'smokes', 'Unknown']
    if data.get('smoking_status') not in valid_smoking:
        errors.append("Invalid smoking status")
    
    # Validate stroke
    if data.get('stroke') not in ['0', '1', 0, 1]:
        errors.append("Stroke must be 0 or 1")
    
    return errors

# Login Required Decorator
def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', '').strip())
        email = sanitize_input(request.form.get('email', '').strip())
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not validate_username(username):
            flash('Username must be 3-20 characters long and contain only letters, numbers, and underscores.', 'danger')
            return redirect(url_for('register'))
        
        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        # Hash password
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Store in SQLite
        try:
            conn = sqlite3.connect(SQLITE_DB)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, password_hash))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', '').strip())
        password = request.form.get('password', '')
        
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[1], password):
            session.permanent = True
            session['user_id'] = user[0]
            session['username'] = username
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                         (datetime.now(), user[0]))
            conn.commit()
            conn.close()
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            conn.close()
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get total patient count
    total_patients = patients_collection.count_documents({})
    stroke_patients = patients_collection.count_documents({'stroke': 1})
    
    return render_template('dashboard.html', 
                         total_patients=total_patients,
                         stroke_patients=stroke_patients)

@app.route('/patients')
@login_required
def patients():
    """View all patients"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get patients from MongoDB
    total = patients_collection.count_documents({})
    patients_list = list(patients_collection.find().skip((page - 1) * per_page).limit(per_page))
    
    # Convert ObjectId to string for rendering
    for patient in patients_list:
        patient['_id'] = str(patient['_id'])
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('patients.html', 
                         patients=patients_list,
                         page=page,
                         total_pages=total_pages)

@app.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        # Collect and sanitize data
        patient_data = {
            'id': int(request.form.get('id')),
            'gender': sanitize_input(request.form.get('gender')),
            'age': float(request.form.get('age')),
            'hypertension': int(request.form.get('hypertension')),
            'heart_disease': int(request.form.get('heart_disease')),
            'ever_married': sanitize_input(request.form.get('ever_married')),
            'work_type': sanitize_input(request.form.get('work_type')),
            'Residence_type': sanitize_input(request.form.get('Residence_type')),
            'avg_glucose_level': float(request.form.get('avg_glucose_level')),
            'bmi': float(request.form.get('bmi')),
            'smoking_status': sanitize_input(request.form.get('smoking_status')),
            'stroke': int(request.form.get('stroke')),
            'created_by': session['username'],
            'created_at': datetime.now()
        }
        
        # Validate data
        errors = validate_patient_data(patient_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('add_patient'))
        
        # Check if patient ID already exists
        if patients_collection.find_one({'id': patient_data['id']}):
            flash('Patient ID already exists.', 'danger')
            return redirect(url_for('add_patient'))
        
        # Insert into MongoDB
        patients_collection.insert_one(patient_data)
        flash('Patient added successfully!', 'success')
        return redirect(url_for('patients'))
    
    return render_template('add_patient.html')

@app.route('/patient/edit/<patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Edit existing patient"""
    from bson.objectid import ObjectId
    
    if request.method == 'POST':
        # Collect and sanitize data
        updated_data = {
            'gender': sanitize_input(request.form.get('gender')),
            'age': float(request.form.get('age')),
            'hypertension': int(request.form.get('hypertension')),
            'heart_disease': int(request.form.get('heart_disease')),
            'ever_married': sanitize_input(request.form.get('ever_married')),
            'work_type': sanitize_input(request.form.get('work_type')),
            'Residence_type': sanitize_input(request.form.get('Residence_type')),
            'avg_glucose_level': float(request.form.get('avg_glucose_level')),
            'bmi': float(request.form.get('bmi')),
            'smoking_status': sanitize_input(request.form.get('smoking_status')),
            'stroke': int(request.form.get('stroke')),
            'updated_by': session['username'],
            'updated_at': datetime.now()
        }
        
        # Validate data
        errors = validate_patient_data(updated_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('edit_patient', patient_id=patient_id))
        
        # Update in MongoDB
        patients_collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$set': updated_data}
        )
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients'))
    
    # GET request - fetch patient data
    patient = patients_collection.find_one({'_id': ObjectId(patient_id)})
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients'))
    
    patient['_id'] = str(patient['_id'])
    return render_template('edit_patient.html', patient=patient)

@app.route('/patient/delete/<patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """Delete patient"""
    from bson.objectid import ObjectId
    
    result = patients_collection.delete_one({'_id': ObjectId(patient_id)})
    if result.deleted_count > 0:
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Patient not found.', 'danger')
    
    return redirect(url_for('patients'))

@app.route('/patient/view/<patient_id>')
@login_required
def view_patient(patient_id):
    """View patient details"""
    from bson.objectid import ObjectId
    
    patient = patients_collection.find_one({'_id': ObjectId(patient_id)})
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients'))
    
    patient['_id'] = str(patient['_id'])
    return render_template('view_patient.html', patient=patient)

@app.route('/import-data', methods=['GET', 'POST'])
@login_required
def import_data():
    """Import CSV data into MongoDB"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('import_data'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('import_data'))
        
        if not file.filename.endswith('.csv'):
            flash('Only CSV files are allowed.', 'danger')
            return redirect(url_for('import_data'))
        
        try:
            # Read CSV
            df = pd.read_csv(file)
            
            # Convert to dict and insert
            records = df.to_dict('records')
            for record in records:
                record['imported_by'] = session['username']
                record['imported_at'] = datetime.now()
            
            patients_collection.insert_many(records)
            flash(f'Successfully imported {len(records)} patient records!', 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            flash(f'Error importing data: {str(e)}', 'danger')
            return redirect(url_for('import_data'))
    
    return render_template('import_data.html')

@app.route('/search')
@login_required
def search():
    """Search patients"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('patients'))
    
    # Search by ID or name-related fields
    try:
        patient_id = int(query)
        results = list(patients_collection.find({'id': patient_id}))
    except ValueError:
        # Search in text fields
        results = list(patients_collection.find({
            '$or': [
                {'gender': {'$regex': query, '$options': 'i'}},
                {'work_type': {'$regex': query, '$options': 'i'}},
                {'smoking_status': {'$regex': query, '$options': 'i'}}
            ]
        }))
    
    for patient in results:
        patient['_id'] = str(patient['_id'])
    
    return render_template('search_results.html', patients=results, query=query)

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_sqlite_db()
    app.run(debug=True, host='0.0.0.0', port=5000)