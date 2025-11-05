"""
User repository for SQLite database operations
"""

from datetime import datetime
import logging
import sqlite3
from typing import Dict, Optional

from flask_login import UserMixin

logger = logging.getLogger(__name__)


class User(UserMixin):
    """User model for Flask-Login"""

    def __init__(
        self,
        user_id,
        username,
        email,
        password_hash,
        created_at=None,
        last_login=None,
        is_active=True,
        role="viewer",
        failed_login_attempts=0,
        locked_until=None,
    ):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.last_login = last_login
        self.role = role
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        # Store is_active as _is_active to avoid property conflict
        self._is_active = is_active

    @property
    def is_active(self):
        """Check if user is active"""
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        """Set user active status"""
        self._is_active = bool(value)

    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.is_active

    def __repr__(self):
        return f"<User {self.username}>"


class UserRepository:
    """Repository for user data operations"""

    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create users table with role support
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    role TEXT DEFAULT 'viewer'
                )
            """
            )

            # Create audit log table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_role ON users(role)")

            conn.commit()
            conn.close()
            logger.info("SQLite database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
            raise

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def create_user(
        self, username: str, email: str, password_hash: str, role: str = "viewer"
    ) -> int:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, role),
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"User created: {username} with role {role}")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed - duplicate entry: {username}")
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_user(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_user(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = self.get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_user(dict(row))
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise

    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ?, failed_login_attempts = 0 WHERE id = ?",
                (datetime.now(), user_id),
            )
            conn.commit()
            conn.close()
            logger.info(f"Updated last login for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            raise

    def increment_failed_login(self, username: str):
        """Increment failed login attempts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                (
                    "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 "
                    "WHERE username = ?"
                ),
                (username,),
            )
            conn.commit()
            conn.close()
            logger.warning(f"Failed login attempt for user: {username}")
        except Exception as e:
            logger.error(f"Error incrementing failed login: {str(e)}")
            raise

    def lock_user(self, username: str, lock_until: datetime):
        """Lock user account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET locked_until = ? WHERE username = ?",
                (lock_until, username),
            )
            conn.commit()
            conn.close()
            logger.warning(f"User locked: {username} until {lock_until}")
        except Exception as e:
            logger.error(f"Error locking user: {str(e)}")
            raise

    def log_action(
        self, user_id: int, action: str, details: str = None, ip_address: str = None
    ):
        """Log user action to audit log"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
                (user_id, action, details, ip_address),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")

    def _row_to_user(self, row: Dict) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=row.get("created_at"),
            last_login=row.get("last_login"),
            is_active=bool(row.get("is_active", 1)),
            role=row.get("role", "viewer"),
            failed_login_attempts=row.get("failed_login_attempts", 0),
            locked_until=row.get("locked_until"),
        )
