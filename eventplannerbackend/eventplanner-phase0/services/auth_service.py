from typing import Dict, Any
from models.user_repository import UserRepository
from utils import hash_password, verify_password

class AuthService:
    
    def __init__(self, user_repository: UserRepository = None):
        self.user_repository = user_repository or UserRepository()
    
    def signup(self, name: str, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()
        hashed_password = hash_password(password)
        
        return self.user_repository.create_user(name, email, hashed_password)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        email = email.strip().lower()
        
        user = self.user_repository.get_user_by_email(email)
        
        if not user or not verify_password(password, user['password']):
            raise ValueError('Invalid email or password')
        
        return {
            'user_id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
