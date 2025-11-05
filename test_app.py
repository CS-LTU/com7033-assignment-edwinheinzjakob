import unittest
import sys
import os
from app import app, init_sqlite_db, validate_email, validate_username, sanitize_input, validate_patient_data
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pymongo import MongoClient

class TestSecurityFunctions(unittest.TestCase):
    """Test security and validation functions"""
    
    def test_validate_email_valid(self):
        """Test valid email addresses"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.com',
            'test123@test-domain.com'
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email), f"Should validate: {email}")
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses"""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user name@example.com',
            'user@.com',
            ''
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email), f"Should reject: {email}")
    
    def test_validate_username_valid(self):
        """Test valid usernames"""
        valid_usernames = [
            'user123',
            'test_user',
            'UserName',
            'abc',
            'user_name_123'
        ]
        for username in valid_usernames:
            self.assertTrue(validate_username(username), f"Should validate: {username}")
    
    def test_validate_username_invalid(self):
        """Test invalid usernames"""
        invalid_usernames = [
            'ab',  # Too short
            'a' * 21,  # Too long
            'user name',  # Contains space
            'user-name',  # Contains hyphen
            'user@name',  # Contains special char
            ''
        ]
        for username in invalid_usernames:
            self.assertFalse(validate_username(username), f"Should reject: {username}")
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        test_cases = [
            ('<script>alert("XSS")</script>', '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'),
            ('Normal text', 'Normal text'),
            ('<b>Bold</b>', '&lt;b&gt;Bold&lt;/b&gt;'),
            ("Test's quote", "Test&#x27;s quote"),
            ('', '')
        ]
        for input_str, expected in test_cases:
            result = sanitize_input(input_str)
            self.assertEqual(result, expected, f"Failed to sanitize: {input_str}")
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePassword123!"
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Should verify correct password
        self.assertTrue(check_password_hash(hashed, password))
        
        # Should reject incorrect password
        self.assertFalse(check_password_hash(hashed, "WrongPassword"))
        
        # Hashed password should not equal original
        self.assertNotEqual(hashed, password)

class TestPatientDataValidation(unittest.TestCase):
    """Test patient data validation"""
    
    def test_validate_patient_data_valid(self):
        """Test valid patient data"""
        valid_data = {
            'age': '45',
            'gender': 'Male',
            'hypertension': '1',
            'heart_disease': '0',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': '106.5',
            'bmi': '28.5',
            'smoking_status': 'never smoked',
            'stroke': '0'
        }
        errors = validate_patient_data(valid_data)
        self.assertEqual(len(errors), 0, f"Should have no errors, got: {errors}")
    
    def test_validate_patient_data_invalid_age(self):
        """Test invalid age values"""
        invalid_ages = ['-5', '150', 'abc']
        for age in invalid_ages:
            data = self._get_base_patient_data()
            data['age'] = age
            errors = validate_patient_data(data)
            self.assertGreater(len(errors), 0, f"Should reject age: {age}")
    
    def test_validate_patient_data_invalid_gender(self):
        """Test invalid gender values"""
        data = self._get_base_patient_data()
        data['gender'] = 'Invalid'
        errors = validate_patient_data(data)
        self.assertGreater(len(errors), 0, "Should reject invalid gender")
    
    def test_validate_patient_data_invalid_glucose(self):
        """Test invalid glucose levels"""
        invalid_glucose = ['-10', '600', 'abc']
        for glucose in invalid_glucose:
            data = self._get_base_patient_data()
            data['avg_glucose_level'] = glucose
            errors = validate_patient_data(data)
            self.assertGreater(len(errors), 0, f"Should reject glucose: {glucose}")
    
    def test_validate_patient_data_invalid_bmi(self):
        """Test invalid BMI values"""
        invalid_bmi = ['-5', '150', 'abc']
        for bmi in invalid_bmi:
            data = self._get_base_patient_data()
            data['bmi'] = bmi
            errors = validate_patient_data(data)
            self.assertGreater(len(errors), 0, f"Should reject BMI: {bmi}")
    
    def _get_base_patient_data(self):
        """Helper method to get valid base patient data"""
        return {
            'age': '45',
            'gender': 'Male',
            'hypertension': '1',
            'heart_disease': '0',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': '106.5',
            'bmi': '28.5',
            'smoking_status': 'never smoked',
            'stroke': '0'
        }

class TestFlaskApp(unittest.TestCase):
    """Test Flask application routes and functionality"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        init_sqlite_db()
    
    def test_index_route(self):
        """Test index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_register_route_get(self):
        """Test register route GET request"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
    
    def test_login_route_get(self):
        """Test login route GET request"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get('/dashboard')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_patients_route_requires_login(self):
        """Test that patients route requires authentication"""
        response = self.client.get('/patients')
        self.assertEqual(response.status_code, 302)
    
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = self.client.post('/register', data={
            'username': 'testuser2',
            'email': 'invalid-email',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email', response.data)
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        response = self.client.post('/register', data={
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'DifferentPass456'
        }, follow_redirects=True)
        self.assertIn(b'do not match', response.data)
    
    def test_register_short_password(self):
        """Test registration with short password"""
        response = self.client.post('/register', data={
            'username': 'testuser4',
            'email': 'test4@example.com',
            'password': 'short',
            'confirm_password': 'short'
        }, follow_redirects=True)
        self.assertIn(b'at least 8 characters', response.data)

class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        init_sqlite_db()
    
    def test_sqlite_connection(self):
        """Test SQLite database connection"""
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()
            conn.close()
            self.assertIsNotNone(result, "Users table should exist")
        except Exception as e:
            self.fail(f"SQLite connection failed: {str(e)}")
    
    def test_mongodb_connection(self):
        """Test MongoDB connection"""
        try:
            client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.server_info()  # Will raise exception if cannot connect
            self.assertTrue(True)
        except Exception as e:
            self.skipTest(f"MongoDB not available: {str(e)}")

class TestCSRFProtection(unittest.TestCase):
    """Test CSRF protection"""
    
    def setUp(self):
        """Set up test client with CSRF enabled"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        self.client = app.test_client()
    
    def test_csrf_protection_enabled(self):
        """Test that CSRF protection is enabled"""
        response = self.client.get('/register')
        self.assertIn(b'csrf_token', response.data)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)