import mysql.connector
from mysql.connector import errorcode
from typing import Optional
import logging
from config import DB_CONFIG
from handlers.exceptions import DatabaseConnectionException

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            autocommit=False
        )
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err.errno} - {err.msg}")
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise DatabaseConnectionException("Database access denied. Please check your credentials.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise DatabaseConnectionException("Database does not exist.")
        else:
            raise DatabaseConnectionException(f"Failed to connect to database: {err.msg}")
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {str(e)}")
        raise DatabaseConnectionException("Failed to connect to database.")

def init_db() -> None:
    """Initialize database with proper error handling"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET 'utf8'")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        logger.info(f"Database '{DB_CONFIG['database']}' created or already exists.")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if the 'name' column exists and add it if it doesn't
        cursor.execute("SHOW COLUMNS FROM `users` LIKE 'name'")
        result = cursor.fetchone()
        if not result:
            cursor.execute("ALTER TABLE `users` ADD COLUMN `name` VARCHAR(255) NOT NULL FIRST")
            logger.info("Column 'name' added to 'users' table.")

        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                location VARCHAR(255) NOT NULL,
                description TEXT,
                organizer_user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_events_organizer FOREIGN KEY (organizer_user_id) REFERENCES users(id) ON DELETE RESTRICT
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8
        ''')

        # Create event_attendees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_attendees (
                id INT PRIMARY KEY AUTO_INCREMENT,
                event_id INT NOT NULL,
                user_id INT NOT NULL,
                role ENUM('organizer','attendee') NOT NULL,
                attendance_status ENUM('pending', 'going', 'maybe', 'not_going') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_attendees_event FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                CONSTRAINT fk_attendees_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uq_event_user (event_id, user_id),
                KEY idx_attendees_user_role (user_id, role),
                KEY idx_attendees_event (event_id)
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8
        ''')
        
        # Check if the 'attendance_status' column exists and add it if it doesn't
        cursor.execute("SHOW COLUMNS FROM `event_attendees` LIKE 'attendance_status'")
        result = cursor.fetchone()
        if not result:
            cursor.execute("ALTER TABLE `event_attendees` ADD COLUMN `attendance_status` ENUM('pending', 'going', 'maybe', 'not_going') DEFAULT 'pending' AFTER role")
            logger.info("Column 'attendance_status' added to 'event_attendees' table.")

        conn.commit()
        logger.info("Database initialized successfully")
        
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        logger.error(f"Database error initializing database: {err}")
        raise DatabaseConnectionException(f"Failed to initialize database: {err.msg}")
    except DatabaseConnectionException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error initializing database: {str(e)}")
        raise DatabaseConnectionException("Failed to initialize database.")
    finally:
        if cursor:
            cursor.close()
        close_db(conn)


def close_db(conn) -> None:
    """Close database connection safely"""
    if conn:
        try:
            conn.close()
        except Exception as e:
            logger.warning(f"Error closing database connection: {str(e)}")
