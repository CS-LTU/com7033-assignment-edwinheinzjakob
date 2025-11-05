"""
Patient service for business logic
"""

import logging
from typing import Any, Dict, List, Optional

from app.repositories.patient_repository import PatientRepository
from app.security.encryption import encryption_service
from app.security.validation import sanitize_input, validate_patient_data

logger = logging.getLogger(__name__)


class PatientService:
    """Service for patient operations"""

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    def create_patient(
        self, patient_data: Dict[str, Any], username: str
    ) -> tuple[bool, str, Optional[str]]:
        """
        Create a new patient record

        Returns:
            (success, message, patient_id)
        """
        # Sanitize input
        sanitized_data = {}
        for key, value in patient_data.items():
            if isinstance(value, str):
                sanitized_data[key] = sanitize_input(value)
            else:
                sanitized_data[key] = value

        # Add metadata
        sanitized_data["created_by"] = username

        # Validate data
        errors = validate_patient_data(sanitized_data)
        if errors:
            return False, "; ".join(errors), None

        # Check if patient ID already exists
        if self.patient_repo.get_patient_by_record_id(int(sanitized_data["id"])):
            return False, "Patient ID already exists.", None

        # Encrypt sensitive fields if encryption service is available
        if encryption_service:
            # Encrypt email if present (example)
            if "email" in sanitized_data and sanitized_data["email"]:
                sanitized_data["email"] = encryption_service.encrypt(
                    sanitized_data["email"]
                )

        # Insert patient
        try:
            patient_id = self.patient_repo.insert_patient(sanitized_data)
            logger.info(f"Patient created: {sanitized_data.get('id')} by {username}")
            return True, "Patient added successfully!", patient_id
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return False, f"Error creating patient: {str(e)}", None

    def update_patient(
        self, patient_id: str, update_data: Dict[str, Any], username: str
    ) -> tuple[bool, str]:
        """
        Update patient record

        Returns:
            (success, message)
        """
        # Sanitize input
        sanitized_data = {}
        for key, value in update_data.items():
            if isinstance(value, str):
                sanitized_data[key] = sanitize_input(value)
            else:
                sanitized_data[key] = value

        sanitized_data["updated_by"] = username

        # Validate data
        errors = validate_patient_data(sanitized_data)
        if errors:
            return False, "; ".join(errors)

        # Encrypt sensitive fields if needed
        if encryption_service and "email" in sanitized_data:
            sanitized_data["email"] = encryption_service.encrypt(
                sanitized_data["email"]
            )

        # Update patient
        try:
            modified = self.patient_repo.update_patient(patient_id, sanitized_data)
            if modified > 0:
                logger.info(f"Patient updated: {patient_id} by {username}")
                return True, "Patient updated successfully!"
            else:
                return False, "Patient not found or no changes made."
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            return False, f"Error updating patient: {str(e)}"

    def delete_patient(self, patient_id: str, username: str) -> tuple[bool, str]:
        """
        Delete patient record

        Returns:
            (success, message)
        """
        try:
            deleted = self.patient_repo.delete_patient(patient_id)
            if deleted > 0:
                logger.info(f"Patient deleted: {patient_id} by {username}")
                return True, "Patient deleted successfully!"
            else:
                return False, "Patient not found."
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            return False, f"Error deleting patient: {str(e)}"

    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        patient = self.patient_repo.get_patient_by_id(patient_id)
        if patient and encryption_service:
            # Decrypt sensitive fields
            if "email" in patient and patient["email"]:
                try:
                    patient["email"] = encryption_service.decrypt(patient["email"])
                except Exception:
                    pass
        return patient

    def get_patients(self, page: int = 1, per_page: int = 20) -> tuple[List[Dict], int]:
        """Get paginated patients"""
        skip = (page - 1) * per_page
        patients = self.patient_repo.get_all_patients(skip, per_page)
        total = self.patient_repo.count_patients()

        # Decrypt sensitive fields
        if encryption_service:
            for patient in patients:
                if "email" in patient and patient["email"]:
                    try:
                        patient["email"] = encryption_service.decrypt(patient["email"])
                    except Exception:
                        pass

        return patients, total

    def search_patients(self, query: str) -> List[Dict]:
        """Search patients"""
        results = self.patient_repo.search_patients(query)

        # Decrypt sensitive fields
        if encryption_service:
            for patient in results:
                if "email" in patient and patient["email"]:
                    try:
                        patient["email"] = encryption_service.decrypt(patient["email"])
                    except Exception:
                        pass

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get patient statistics"""
        return self.patient_repo.get_statistics()

    def import_patients(
        self, patients_list: List[Dict], username: str
    ) -> tuple[bool, str, int]:
        """
        Bulk import patients

        Returns:
            (success, message, count)
        """
        # Validate and sanitize each patient
        valid_patients = []
        errors = []

        for idx, patient in enumerate(patients_list):
            # Sanitize
            sanitized = {}
            for key, value in patient.items():
                if isinstance(value, str):
                    sanitized[key] = sanitize_input(value)
                else:
                    sanitized[key] = value

            # Validate
            validation_errors = validate_patient_data(sanitized)
            if validation_errors:
                errors.append(f"Row {idx + 1}: {', '.join(validation_errors)}")
                continue

            sanitized["imported_by"] = username
            valid_patients.append(sanitized)

        if not valid_patients:
            return False, "No valid patients to import. " + "; ".join(errors[:5]), 0

        # Encrypt sensitive fields
        if encryption_service:
            for patient in valid_patients:
                if "email" in patient and patient.get("email"):
                    patient["email"] = encryption_service.encrypt(patient["email"])

        # Import
        try:
            count = self.patient_repo.bulk_insert_patients(valid_patients)
            logger.info(f"Imported {count} patients by {username}")
            error_msg = f" ({len(errors)} errors)" if errors else ""
            return (
                True,
                f"Successfully imported {count} patient records!{error_msg}",
                count,
            )
        except Exception as e:
            logger.error(f"Error importing patients: {str(e)}")
            return False, f"Error importing patients: {str(e)}", 0
