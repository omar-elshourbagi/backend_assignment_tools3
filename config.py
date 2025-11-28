import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eventplanner.db")

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "eventplanner"
}

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
