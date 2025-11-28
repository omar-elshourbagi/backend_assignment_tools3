from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal
from datetime import date as Date, time as Time

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

class UserInfo(BaseModel):
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User email")

class LoginResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User email")
    token: str = Field(..., description="JWT access token")
    message: str = Field(..., description="Response message")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")

# Event schemas
class EventCreateRequest(BaseModel):
    title: str = Field(..., description="Event title", example="Meetup")
    date: Date = Field(..., description="Event date", example="2025-12-05")
    time: Time = Field(..., description="Event time", example="18:00")
    location: str = Field(..., description="Event location", example="Cairo")
    description: Optional[str] = Field(None, description="Event description", example="Monthly meetup")

class Attendee(BaseModel):
    user_id: int = Field(..., description="User ID")
    role: Literal['organizer', 'attendee'] = Field(..., description="Attendee role")
    attendance_status: Literal['pending', 'going', 'maybe', 'not_going'] = Field(default='pending', description="Attendance status")

class EventResponse(BaseModel):
    id: int = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    date: Date = Field(..., description="Event date")
    time: Time = Field(..., description="Event time")
    location: str = Field(..., description="Event location")
    description: Optional[str] = Field(None, description="Event description")
    organizer_user_id: int = Field(..., description="Organizer user ID")
    attendees: List[Attendee] = Field(default_factory=list, description="List of attendees")

class InviteRequest(BaseModel):
    userId: int = Field(..., description="User ID to invite", example=2)

class AttendanceStatusUpdate(BaseModel):
    status: Literal['pending', 'going', 'maybe', 'not_going'] = Field(..., description="Attendance status", example="going")

class InvitationInfo(BaseModel):
    event_id: int = Field(..., description="Event ID")
    event_title: str = Field(..., description="Event title")
    event_date: Date = Field(..., description="Event date")
    invited_user_id: int = Field(..., description="Invited user's ID")
    invited_user_name: str = Field(..., description="Invited user's name")
    invited_user_email: str = Field(..., description="Invited user's email")
    attendance_status: Literal['pending', 'going', 'maybe', 'not_going'] = Field(..., description="Invitation status")

