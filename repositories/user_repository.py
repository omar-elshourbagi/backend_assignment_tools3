import mysql.connector
from typing import Optional, Dict, Any
from database import get_db_connection, close_db
from config import DB_CONFIG

class UserRepository:
    
    @staticmethod
    def create_user(name: str, email: str, hashed_password: str) -> Dict[str, Any]:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")
        
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                (name, email, hashed_password)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                'user_id': user_id,
                'name': name,
                'email': email
            }
        
        except mysql.connector.Error as err:
            if err.errno == 1062:
                raise ValueError('Email already registered')
            raise Exception(f"Database error: {err}")
        
        finally:
            cursor.close()
            close_db(conn)
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            return user if user else None
        
        finally:
            cursor.close()
            close_db(conn)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            return user if user else None
        
        finally:
            cursor.close()
            close_db(conn)
    
    @staticmethod
    def user_exists(email: str) -> bool:
        user = UserRepository.get_user_by_email(email)
        return user is not None
