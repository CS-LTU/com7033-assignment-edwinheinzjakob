"""
End-to-end tests for web application
"""
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    return create_app('testing')

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestWebApplication:
    """E2E tests for web application"""
    
    def test_home_page(self, client):
        """Test home page loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_register_page(self, client):
        """Test registration page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
    
    def test_register_user(self, client):
        """Test user registration flow"""
        response = client.post('/auth/register', data={
            'username': 'e2etest',
            'email': 'e2e@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to login after registration
        assert b'login' in response.data.lower() or b'success' in response.data.lower()
    
    def test_login_logout(self, client):
        """Test login and logout flow"""
        # Register user first
        client.post('/auth/register', data={
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
        })
        
        # Login
        response = client.post('/auth/login', data={
            'username': 'logintest',
            'password': 'SecurePass123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200

class TestAPIE2E:
    """E2E tests for API"""
    
    def test_api_login(self, client):
        """Test API login endpoint"""
        # Register user first
        from app.repositories.user_repository import UserRepository
        from app.security.password import password_service
        
        user_repo = UserRepository()
        password_hash = password_service.hash_password('SecurePass123!')
        user_repo.create_user('apitest', 'api@example.com', password_hash)
        
        # Login via API
        response = client.post('/api/v1/auth/login', json={
            'username': 'apitest',
            'password': 'SecurePass123!'
        })
        
        assert response.status_code == 200
        assert 'token' in response.json
        assert response.json['success'] is True
    
    def test_api_get_patients(self, client):
        """Test API get patients endpoint"""
        # Get auth token
        from app.repositories.user_repository import UserRepository
        from app.security.password import password_service
        
        user_repo = UserRepository()
        password_hash = password_service.hash_password('SecurePass123!')
        user_repo.create_user('apitest2', 'api2@example.com', password_hash)
        
        # Login
        login_response = client.post('/api/v1/auth/login', json={
            'username': 'apitest2',
            'password': 'SecurePass123!'
        })
        token = login_response.json['token']
        
        # Get patients
        response = client.get('/api/v1/patients', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'data' in response.json

