"""
Unit tests for security functions
"""

import pytest

from app.security.password import password_service
from app.security.validation import (sanitize_input, validate_email,
                                     validate_password_strength,
                                     validate_patient_data, validate_username)


class TestEmailValidation:
    """Test email validation"""

    def test_valid_emails(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.com",
            "test123@test-domain.com",
        ]
        for email in valid_emails:
            assert validate_email(email), f"Should validate: {email}"

    def test_invalid_emails(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user name@example.com",
            "user@.com",
            "",
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Should reject: {email}"


class TestUsernameValidation:
    """Test username validation"""

    def test_valid_usernames(self):
        """Test valid usernames"""
        valid_usernames = ["user123", "test_user", "UserName", "abc", "user_name_123"]
        for username in valid_usernames:
            assert validate_username(username), f"Should validate: {username}"

    def test_invalid_usernames(self):
        """Test invalid usernames"""
        invalid_usernames = [
            "ab",  # Too short
            "a" * 21,  # Too long
            "user name",  # Contains space
            "user-name",  # Contains hyphen
            "user@name",  # Contains special char
            "",
        ]
        for username in invalid_usernames:
            assert not validate_username(username), f"Should reject: {username}"


class TestInputSanitization:
    """Test input sanitization"""

    def test_sanitize_xss(self):
        """Test XSS prevention"""
        test_cases = [
            (
                '<script>alert("XSS")</script>',
                "&lt;script&gt;alert(&quot;XSS&quot;)&lt;&#x2F;script&gt;",
            ),
            ("Normal text", "Normal text"),
            ("<b>Bold</b>", "&lt;b&gt;Bold&lt;&#x2F;b&gt;"),
            ("Test's quote", "Test&#x27;s quote"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            result = sanitize_input(input_str)
            assert result == expected, f"Failed to sanitize: {input_str}"


class TestPasswordHashing:
    """Test password hashing"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePassword123!"
        hashed = password_service.hash_password(password)

        # Should verify correct password
        assert password_service.verify_password(hashed, password)

        # Should reject incorrect password
        assert not password_service.verify_password(hashed, "WrongPassword")

        # Hashed password should not equal original
        assert hashed != password


class TestPatientDataValidation:
    """Test patient data validation"""

    def test_valid_patient_data(self):
        """Test valid patient data"""
        valid_data = {
            "age": 45.0,
            "gender": "Male",
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 106.5,
            "bmi": 28.5,
            "smoking_status": "never smoked",
            "stroke": 0,
        }
        errors = validate_patient_data(valid_data)
        assert len(errors) == 0, f"Should have no errors, got: {errors}"

    def test_invalid_age(self):
        """Test invalid age values"""
        invalid_ages = [-5, 150, "abc"]
        for age in invalid_ages:
            data = self._get_base_patient_data()
            data["age"] = age
            errors = validate_patient_data(data)
            assert len(errors) > 0, f"Should reject age: {age}"

    def test_invalid_gender(self):
        """Test invalid gender values"""
        data = self._get_base_patient_data()
        data["gender"] = "Invalid"
        errors = validate_patient_data(data)
        assert len(errors) > 0, "Should reject invalid gender"

    def test_password_strength(self):
        """Test password strength validation"""
        is_valid, errors = validate_password_strength("weak")
        assert not is_valid
        assert len(errors) > 0

        is_valid, errors = validate_password_strength("StrongPass123!")
        assert is_valid
        assert len(errors) == 0

    def _get_base_patient_data(self):
        """Helper method to get valid base patient data"""
        return {
            "age": 45.0,
            "gender": "Male",
            "hypertension": 1,
            "heart_disease": 0,
            "ever_married": "Yes",
            "work_type": "Private",
            "Residence_type": "Urban",
            "avg_glucose_level": 106.5,
            "bmi": 28.5,
            "smoking_status": "never smoked",
            "stroke": 0,
        }
