import mysql.connector
from typing import Optional, Dict, Any, List
import logging
from database import get_db_connection, close_db
from config import DB_CONFIG
from handlers.exceptions import DatabaseException, ConflictException

logger = logging.getLogger(__name__)

class UserRepository:
    
    @staticmethod
    def create_user(name: str, email: str, hashed_password: str) -> Dict[str, Any]:
        """Create a new user with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                (name, email, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            logger.info(f"User created successfully: {user_id}")
            
            return {
                'user_id': user_id,
                'name': name,
                'email': email
            }
        
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            if err.errno == 1062:  # Duplicate entry
                raise ConflictException('Email already registered')
            logger.error(f"Database error creating user: {err}")
            raise DatabaseException(f"Failed to create user: {err.msg}")
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error creating user: {str(e)}")
            raise DatabaseException("Failed to create user")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            return user if user else None
        
        except mysql.connector.Error as err:
            logger.error(f"Database error getting user by email: {err}")
            raise DatabaseException(f"Failed to retrieve user: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by email: {str(e)}")
            raise DatabaseException("Failed to retrieve user")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            return user if user else None
        
        except mysql.connector.Error as err:
            logger.error(f"Database error getting user by ID: {err}")
            raise DatabaseException(f"Failed to retrieve user: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting user by ID: {str(e)}")
            raise DatabaseException("Failed to retrieve user")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)
    
    @staticmethod
    def user_exists(email: str) -> bool:
        user = UserRepository.get_user_by_email(email)
        return user is not None

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        """Get all users from the database with proper error handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute('SELECT id, name, email, created_at FROM users ORDER BY created_at DESC')
            users = cursor.fetchall() or []
            
            return list(users)
        
        except mysql.connector.Error as err:
            logger.error(f"Database error getting all users: {err}")
            raise DatabaseException(f"Failed to retrieve users: {err.msg}")
        except Exception as e:
            logger.error(f"Unexpected error getting all users: {str(e)}")
            raise DatabaseException("Failed to retrieve users")
        finally:
            if cursor:
                cursor.close()
            close_db(conn)
