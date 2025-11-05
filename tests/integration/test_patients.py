"""
Integration tests for patient operations
"""

import pytest
from app.repositories.patient_repository import PatientRepository
from app.services.patient_service import PatientService


class TestPatientService:
    """Test patient service"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.patient_repo = PatientRepository()
        self.patient_service = PatientService(self.patient_repo)

    def test_create_patient(self, sample_patient):
        """Test patient creation"""
        success, message, patient_id = self.patient_service.create_patient(
            sample_patient, "testuser"
        )

        assert success
        assert patient_id is not None
        assert "successfully" in message.lower()

    def test_get_patient(self, sample_patient):
        """Test getting patient"""
        # Create patient first
        _, _, patient_id = self.patient_service.create_patient(
            sample_patient, "testuser"
        )

        # Get patient
        patient = self.patient_service.get_patient(patient_id)

        assert patient is not None
        assert patient["id"] == sample_patient["id"]

    def test_update_patient(self, sample_patient):
        """Test patient update"""
        # Create patient
        _, _, patient_id = self.patient_service.create_patient(
            sample_patient, "testuser"
        )

        # Update patient
        update_data = {"age": 50.0, "bmi": 30.0}
        success, message = self.patient_service.update_patient(
            patient_id, update_data, "testuser"
        )

        assert success
        assert "successfully" in message.lower()

        # Verify update
        patient = self.patient_service.get_patient(patient_id)
        assert patient["age"] == 50.0
        assert patient["bmi"] == 30.0

    def test_delete_patient(self, sample_patient):
        """Test patient deletion"""
        # Create patient
        _, _, patient_id = self.patient_service.create_patient(
            sample_patient, "testuser"
        )

        # Delete patient
        success, message = self.patient_service.delete_patient(patient_id, "testuser")

        assert success
        assert "successfully" in message.lower()

        # Verify deletion
        patient = self.patient_service.get_patient(patient_id)
        assert patient is None

    def test_search_patients(self, sample_patient):
        """Test patient search"""
        # Create patient
        self.patient_service.create_patient(sample_patient, "testuser")

        # Search by ID
        results = self.patient_service.search_patients(str(sample_patient["id"]))
        assert len(results) > 0

        # Search by text
        results = self.patient_service.search_patients("Male")
        assert len(results) > 0
