"""
Patient repository for MongoDB operations
"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional, Any
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

class PatientRepository:
    """Repository for patient data operations"""
    
    def __init__(self, uri='mongodb://localhost:27017/', db_name='stroke_prediction_db'):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.patients = self.db['patients']
            
            # Test connection
            self.client.server_info()
            
            # Create indexes
            self.create_indexes()
            
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            self.patients.create_index('id', unique=True)
            self.patients.create_index('gender')
            self.patients.create_index('stroke')
            self.patients.create_index('age')
            self.patients.create_index('work_type')
            self.patients.create_index('smoking_status')
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def insert_patient(self, patient_data: Dict[str, Any]) -> str:
        """Insert a new patient record"""
        try:
            patient_data['created_at'] = datetime.now()
            result = self.patients.insert_one(patient_data)
            logger.info(f"Patient inserted: ID {patient_data.get('id')}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting patient: {str(e)}")
            raise
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by database ID (ObjectId)"""
        try:
            return self.patients.find_one({'_id': ObjectId(patient_id)})
        except Exception as e:
            logger.error(f"Error fetching patient: {str(e)}")
            return None
    
    def get_patient_by_record_id(self, record_id: int) -> Optional[Dict]:
        """Get patient by record ID"""
        try:
            return self.patients.find_one({'id': int(record_id)})
        except Exception as e:
            logger.error(f"Error fetching patient: {str(e)}")
            return None
    
    def update_patient(self, patient_id: str, update_data: Dict[str, Any]) -> int:
        """Update patient record"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.patients.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': update_data}
            )
            logger.info(f"Patient updated: {patient_id}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            raise
    
    def delete_patient(self, patient_id: str) -> int:
        """Delete patient record"""
        try:
            result = self.patients.delete_one({'_id': ObjectId(patient_id)})
            logger.info(f"Patient deleted: {patient_id}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            raise
    
    def get_all_patients(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get all patients with pagination"""
        try:
            patients = list(self.patients.find().skip(skip).limit(limit).sort('created_at', -1))
            # Convert ObjectId to string for JSON serialization
            for patient in patients:
                patient['_id'] = str(patient['_id'])
            return patients
        except Exception as e:
            logger.error(f"Error fetching patients: {str(e)}")
            return []
    
    def count_patients(self, query: Optional[Dict] = None) -> int:
        """Count total patients"""
        try:
            if query:
                return self.patients.count_documents(query)
            return self.patients.count_documents({})
        except Exception as e:
            logger.error(f"Error counting patients: {str(e)}")
            return 0
    
    def search_patients(self, search_query: str) -> List[Dict]:
        """Search patients by various criteria"""
        try:
            # Try to search by ID first
            try:
                patient_id = int(search_query)
                results = list(self.patients.find({'id': patient_id}))
                if results:
                    for patient in results:
                        patient['_id'] = str(patient['_id'])
                    return results
            except ValueError:
                pass
            
            # Text search
            query = {
                '$or': [
                    {'gender': {'$regex': search_query, '$options': 'i'}},
                    {'work_type': {'$regex': search_query, '$options': 'i'}},
                    {'smoking_status': {'$regex': search_query, '$options': 'i'}},
                    {'Residence_type': {'$regex': search_query, '$options': 'i'}}
                ]
            }
            results = list(self.patients.find(query))
            for patient in results:
                patient['_id'] = str(patient['_id'])
            return results
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            total = self.count_patients()
            stroke_patients = self.count_patients({'stroke': 1})
            male_count = self.count_patients({'gender': 'Male'})
            female_count = self.count_patients({'gender': 'Female'})
            
            # Average age
            pipeline = [
                {'$group': {'_id': None, 'avg_age': {'$avg': '$age'}}}
            ]
            avg_age_result = list(self.patients.aggregate(pipeline))
            avg_age = avg_age_result[0]['avg_age'] if avg_age_result else 0
            
            return {
                'total_patients': total,
                'stroke_patients': stroke_patients,
                'male_count': male_count,
                'female_count': female_count,
                'average_age': round(avg_age, 2)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def bulk_insert_patients(self, patients_list: List[Dict]) -> int:
        """Bulk insert patient records"""
        try:
            for patient in patients_list:
                patient['imported_at'] = datetime.now()
            result = self.patients.insert_many(patients_list, ordered=False)
            logger.info(f"Bulk inserted {len(result.inserted_ids)} patients")
            return len(result.inserted_ids)
        except Exception as e:
            logger.error(f"Error bulk inserting patients: {str(e)}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")

