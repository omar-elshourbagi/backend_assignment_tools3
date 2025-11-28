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

    conn.commit()
    print("Database initialized successfully")
    cursor.close()
    conn.close()


def close_db(conn) -> None:
    if conn:
        conn.close()
