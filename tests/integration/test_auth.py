"""
Integration tests for authentication
"""
import pytest
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.security.password import password_service

class TestAuthService:
    """Test authentication service"""
    
    def test_register_user(self):
        """Test user registration"""
        user_repo = UserRepository('test_users.db')
        auth_service = AuthService(user_repo)
        
        success, message, user_id = auth_service.register_user(
            'testuser', 'test@example.com', 'SecurePass123!', 'viewer'
        )
        
        assert success
        assert user_id is not None
        assert 'successful' in message.lower()
        
        # Cleanup
        import os
        if os.path.exists('test_users.db'):
            os.remove('test_users.db')
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        user_repo = UserRepository('test_users.db')
        auth_service = AuthService(user_repo)
        
        # Register first user
        auth_service.register_user('testuser', 'test1@example.com', 'SecurePass123!')
        
        # Try to register with same username
        success, message, _ = auth_service.register_user(
            'testuser', 'test2@example.com', 'SecurePass123!'
        )
        
        assert not success
        assert 'already exists' in message.lower()
        
        # Cleanup
        import os
        if os.path.exists('test_users.db'):
            os.remove('test_users.db')
    
    def test_authenticate_user(self):
        """Test user authentication"""
        user_repo = UserRepository('test_users.db')
        auth_service = AuthService(user_repo)
        
        # Register user
        auth_service.register_user('testuser', 'test@example.com', 'SecurePass123!')
        
        # Authenticate
        success, message, user = auth_service.authenticate_user('testuser', 'SecurePass123!')
        
        assert success
        assert user is not None
        assert user.username == 'testuser'
        
        # Cleanup
        import os
        if os.path.exists('test_users.db'):
            os.remove('test_users.db')
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password"""
        user_repo = UserRepository('test_users.db')
        auth_service = AuthService(user_repo)
        
        # Register user
        auth_service.register_user('testuser', 'test@example.com', 'SecurePass123!')
        
        # Try wrong password
        success, message, user = auth_service.authenticate_user('testuser', 'WrongPassword')
        
        assert not success
        assert user is None
        
        # Cleanup
        import os
        if os.path.exists('test_users.db'):
            os.remove('test_users.db')

