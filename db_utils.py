import sqlite3
from pymongo import MongoClient
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SQLiteDB:
    """SQLite database utility class for user authentication"""
    
    def __init__(self, db_path='users.db'):
        """Initialize SQLite database connection"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_username ON users(username)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email ON users(email)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_user(self, username, email, password_hash):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"User created: {username}")
            return user_id
        except sqlite3.IntegrityError as e:
            logger.warning(f"User creation failed - duplicate entry: {username}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET last_login = ?, failed_login_attempts = 0 WHERE id = ?',
                (datetime.now(), user_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"Updated last login for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise
    
    def increment_failed_login(self, username):
        """Increment failed login attempts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE username = ?',
                (username,)
            )
            conn.commit()
            conn.close()
            logger.warning(f"Failed login attempt for user: {username}")
        except Exception as e:
            logger.error(f"Error incrementing failed login: {str(e)}")
            raise
    
    def log_action(self, user_id, action, details=None, ip_address=None):
        """Log user action to audit log"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)',
                (user_id, action, details, ip_address)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")

class MongoDB:
    """MongoDB utility class for patient records"""
    
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
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def insert_patient(self, patient_data):
        """Insert a new patient record"""
        try:
            patient_data['created_at'] = datetime.now()
            result = self.patients.insert_one(patient_data)
            logger.info(f"Patient inserted: ID {patient_data.get('id')}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting patient: {str(e)}")
            raise
    
    def get_patient_by_id(self, patient_id):
        """Get patient by database ID"""
        try:
            from bson.objectid import ObjectId
            return self.patients.find_one({'_id': ObjectId(patient_id)})
        except Exception as e:
            logger.error(f"Error fetching patient: {str(e)}")
            return None
    
    def get_patient_by_record_id(self, record_id):
        """Get patient by record ID"""
        try:
            return self.patients.find_one({'id': int(record_id)})
        except Exception as e:
            logger.error(f"Error fetching patient: {str(e)}")
            return None
    
    def update_patient(self, patient_id, update_data):
        """Update patient record"""
        try:
            from bson.objectid import ObjectId
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
    
    def delete_patient(self, patient_id):
        """Delete patient record"""
        try:
            from bson.objectid import ObjectId
            result = self.patients.delete_one({'_id': ObjectId(patient_id)})
            logger.info(f"Patient deleted: {patient_id}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            raise
    
    def get_all_patients(self, skip=0, limit=20):
        """Get all patients with pagination"""
        try:
            return list(self.patients.find().skip(skip).limit(limit))
        except Exception as e:
            logger.error(f"Error fetching patients: {str(e)}")
            return []
    
    def count_patients(self, query=None):
        """Count total patients"""
        try:
            if query:
                return self.patients.count_documents(query)
            return self.patients.count_documents({})
        except Exception as e:
            logger.error(f"Error counting patients: {str(e)}")
            return 0
    
    def search_patients(self, search_query):
        """Search patients by various criteria"""
        try:
            # Try to search by ID first
            try:
                patient_id = int(search_query)
                results = list(self.patients.find({'id': patient_id}))
                if results:
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
            return list(self.patients.find(query))
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def get_statistics(self):
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
    
    def bulk_insert_patients(self, patients_list):
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