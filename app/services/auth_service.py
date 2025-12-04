"""
Authentication service
"""
from datetime import datetime, timedelta
from flask import request
from flask_login import login_user
import logging

from app.repositories.user_repository import UserRepository, User
from app.security.password import password_service
from app.security.validation import validate_email, validate_username, validate_password_strength

logger = logging.getLogger(__name__)

class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register_user(self, username: str, email: str, password: str, role: str = 'viewer') -> tuple[bool, str, int]:
        """
        Register a new user
        
        Returns:
            (success, message, user_id)
        """
        # Validate inputs
        if not validate_username(username):
            return False, "Username must be 3-20 characters long and contain only letters, numbers, and underscores.", None
        
        if not validate_email(email):
            return False, "Invalid email format.", None
        
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            return False, "; ".join(errors), None
        
        # Check if user exists
        if self.user_repo.get_user_by_username(username):
            return False, "Username already exists.", None
        
        if self.user_repo.get_user_by_email(email):
            return False, "Email already exists.", None
        
        # Hash password
        try:
            password_hash = password_service.hash_password(password)
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            return False, "Error processing registration. Please try again.", None
        
        # Create user
        try:
            user_id = self.user_repo.create_user(username, email, password_hash, role)
            
            # Log action
            self.user_repo.log_action(
                user_id,
                'USER_REGISTERED',
                f'User {username} registered',
                request.remote_addr
            )
            
            logger.info(f"User registered: {username}")
            return True, "Registration successful! Please log in.", user_id
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False, "Error creating account. Please try again.", None
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str, 'User']:
        """
        Authenticate a user
        
        Returns:
            (success, message, user)
        """
        # Get user
        user = self.user_repo.get_user_by_username(username)
        if not user:
            self.user_repo.increment_failed_login(username)
            return False, "Invalid username or password.", None
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            return False, "Account is temporarily locked due to too many failed login attempts.", None
        
        # Check if account is active
        if not user.is_active:
            return False, "Account is inactive. Please contact administrator.", None
        
        # Verify password
        if not password_service.verify_password(user.password_hash, password):
            self.user_repo.increment_failed_login(username)
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts + 1 >= 5:
                lock_until = datetime.now() + timedelta(minutes=15)
                self.user_repo.lock_user(username, lock_until)
                return False, "Too many failed login attempts. Account locked for 15 minutes.", None
            
            return False, "Invalid username or password.", None
        
        # Check if password needs rehashing
        if password_service.check_needs_rehash(user.password_hash):
            # Update password hash (would need to add method to repo)
            pass
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        # Log action
        self.user_repo.log_action(
            user.id,
            'USER_LOGIN',
            f'User {username} logged in',
            request.remote_addr
        )
        
        logger.info(f"User logged in: {username}")
        return True, "Login successful!", user

