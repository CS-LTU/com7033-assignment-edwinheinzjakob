"""
Pytest configuration and fixtures
"""

import pytest
import os
import tempfile
import shutil
from app import create_app
from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.security.password import password_service


@pytest.fixture
def app():
    """Create application for testing"""
    # Use testing configuration
    app = create_app("testing")

    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    app.config["SQLITE_DB"] = db_path

    with app.app_context():
        # Initialize databases
        user_repo = UserRepository(db_path)
        yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for API tests"""
    # Register test user
    user_repo = UserRepository()
    password_hash = password_service.hash_password("testpass123")
    user_id = user_repo.create_user(
        "testuser", "test@example.com", password_hash, "admin"
    )

    # Login via API
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "testpass123"}
    )

    if response.status_code == 200:
        token = response.json["token"]
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
def sample_patient():
    """Sample patient data"""
    return {
        "id": 12345,
        "gender": "Male",
        "age": 45.0,
        "hypertension": 0,
        "heart_disease": 0,
        "ever_married": "Yes",
        "work_type": "Private",
        "Residence_type": "Urban",
        "avg_glucose_level": 106.5,
        "bmi": 28.5,
        "smoking_status": "never smoked",
        "stroke": 0,
    }
