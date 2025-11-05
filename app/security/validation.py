"""
Input validation and sanitization utilities
"""
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> bool:
    """Validate username (alphanumeric and underscore only, 3-20 chars)"""
    if not username:
        return False
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def sanitize_input(data: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not isinstance(data, str):
        return data
    return (data
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;')
            .replace('/', '&#x2F;'))

def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate patient data fields"""
    errors = []
    
    # Validate age
    try:
        age = float(data.get('age', 0))
        if age < 0 or age > 120:
            errors.append("Age must be between 0 and 120")
    except (ValueError, TypeError):
        errors.append("Age must be a valid number")
    
    # Validate gender
    valid_genders = ['Male', 'Female', 'Other']
    if data.get('gender') not in valid_genders:
        errors.append(f"Gender must be one of: {', '.join(valid_genders)}")
    
    # Validate hypertension
    hypertension = data.get('hypertension')
    if str(hypertension) not in ['0', '1']:
        errors.append("Hypertension must be 0 or 1")
    
    # Validate heart_disease
    heart_disease = data.get('heart_disease')
    if str(heart_disease) not in ['0', '1']:
        errors.append("Heart disease must be 0 or 1")
    
    # Validate ever_married
    if data.get('ever_married') not in ['Yes', 'No']:
        errors.append("Ever married must be Yes or No")
    
    # Validate work_type
    valid_work_types = ['Children', 'Govt_job', 'Never_worked', 'Private', 'Self-employed']
    if data.get('work_type') not in valid_work_types:
        errors.append(f"Work type must be one of: {', '.join(valid_work_types)}")
    
    # Validate residence_type
    if data.get('Residence_type') not in ['Rural', 'Urban']:
        errors.append("Residence type must be Rural or Urban")
    
    # Validate avg_glucose_level
    try:
        glucose = float(data.get('avg_glucose_level', 0))
        if glucose < 0 or glucose > 500:
            errors.append("Average glucose level must be between 0 and 500")
    except (ValueError, TypeError):
        errors.append("Average glucose level must be a valid number")
    
    # Validate BMI
    try:
        bmi = float(data.get('bmi', 0))
        if bmi < 0 or bmi > 100:
            errors.append("BMI must be between 0 and 100")
    except (ValueError, TypeError):
        errors.append("BMI must be a valid number")
    
    # Validate smoking_status
    valid_smoking = ['formerly smoked', 'never smoked', 'smokes', 'Unknown']
    smoking_status = data.get('smoking_status', '').lower()
    if smoking_status not in [s.lower() for s in valid_smoking]:
        errors.append(f"Smoking status must be one of: {', '.join(valid_smoking)}")
    
    # Validate stroke
    stroke = data.get('stroke')
    if str(stroke) not in ['0', '1']:
        errors.append("Stroke must be 0 or 1")
    
    return errors

def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """
    Validate password strength
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors

