import mysql.connector
from mysql.connector import errorcode
from typing import Optional
from config import DB_CONFIG

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

def init_db() -> None:
    conn = get_db_connection()
    if not conn:
        print("Could not connect to MySQL.")
        return

    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET 'utf8'")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

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
        print("Column 'name' added to 'users' table.")

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
        print("Column 'attendance_status' added to 'event_attendees' table.")

    conn.commit()
    print("Database initialized successfully")
    cursor.close()
    conn.close()


def close_db(conn) -> None:
    if conn:
        conn.close()
