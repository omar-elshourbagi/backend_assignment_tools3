import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eventplanner.db")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "eventplanner"
}

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
