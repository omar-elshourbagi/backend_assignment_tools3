import os

# ==============================
# Database configuration
# ==============================

DB_CONFIG = {
    # اسم Service بتاع MySQL في OpenShift (مش localhost)
    "host": os.getenv("DB_HOST", "eventplanner-db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "eventplanner"),
}

# لو في أي كود قديم بيستخدم DATABASE_URL (مش أساسي هنا)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ==============================
# App configuration
# ==============================

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# ==============================
# JWT configuration
# ==============================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
