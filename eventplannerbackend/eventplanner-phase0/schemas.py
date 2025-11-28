from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class SignUpRequest(BaseModel):
    name: str = Field(..., description="User's full name", example="John Doe")
    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)", example="password123")
    confirm_password: str = Field(..., description="Confirm user password", example="password123")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    password: str = Field(..., description="User password", example="password123")

class UserResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User email")
    message: str = Field(..., description="Response message")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
