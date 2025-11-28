from typing import Dict, Any
import logging
from models.user_repository import UserRepository
from utils import hash_password, verify_password
from handlers.exceptions import AuthenticationException, NotFoundException, ValidationException
from validators import validate_email, validate_password, validate_name

logger = logging.getLogger(__name__)

class AuthService:
    
    def __init__(self, user_repository: UserRepository = None):
        self.user_repository = user_repository or UserRepository()
    
    def signup(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user with validation"""
        # Validate inputs
        name = validate_name(name)
        email = validate_email(email)
        validate_password(password)
        
        # Hash password
        hashed_password = hash_password(password)
        
        try:
            user = self.user_repository.create_user(name, email, hashed_password)
            logger.info(f"User signed up successfully: {user['user_id']}")
            return user
        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            raise
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with validation"""
        # Validate inputs
        email = validate_email(email)
        if not password or not isinstance(password, str):
            raise ValidationException("Password is required")
        
        user = self.user_repository.get_user_by_email(email)
        
        if not user:
            raise AuthenticationException('Invalid email or password')
        
        if not verify_password(password, user['password']):
            raise AuthenticationException('Invalid email or password')
        
        logger.info(f"User logged in successfully: {user['id']}")
        return {
            'user_id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
