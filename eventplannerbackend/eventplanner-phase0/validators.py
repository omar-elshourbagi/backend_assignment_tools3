"""Input validation utilities"""

from datetime import date, time
from typing import Optional
from handlers.exceptions import ValidationException


def validate_email(email: str) -> str:
    """Validate and normalize email address"""
    if not email or not isinstance(email, str):
        raise ValidationException("Email is required")
    
    email = email.strip().lower()
    
    if not email:
        raise ValidationException("Email cannot be empty")
    
    if "@" not in email or "." not in email.split("@")[1]:
        raise ValidationException("Invalid email format")
    
    if len(email) > 255:
        raise ValidationException("Email is too long (max 255 characters)")
    
    return email


def validate_password(password: str) -> None:
    """Validate password strength"""
    if not password or not isinstance(password, str):
        raise ValidationException("Password is required")
    
    if len(password) < 6:
        raise ValidationException("Password must be at least 6 characters long")
    
    if len(password) > 100:
        raise ValidationException("Password is too long (max 100 characters)")


def validate_name(name: str) -> str:
    """Validate and normalize name"""
    if not name or not isinstance(name, str):
        raise ValidationException("Name is required")
    
    name = name.strip()
    
    if not name:
        raise ValidationException("Name cannot be empty")
    
    if len(name) > 255:
        raise ValidationException("Name is too long (max 255 characters)")
    
    if len(name) < 2:
        raise ValidationException("Name must be at least 2 characters long")
    
    return name


def validate_title(title: str) -> str:
    """Validate event title"""
    if not title or not isinstance(title, str):
        raise ValidationException("Event title is required")
    
    title = title.strip()
    
    if not title:
        raise ValidationException("Event title cannot be empty")
    
    if len(title) > 255:
        raise ValidationException("Event title is too long (max 255 characters)")
    
    return title


def validate_location(location: str) -> str:
    """Validate event location"""
    if not location or not isinstance(location, str):
        raise ValidationException("Event location is required")
    
    location = location.strip()
    
    if not location:
        raise ValidationException("Event location cannot be empty")
    
    if len(location) > 255:
        raise ValidationException("Event location is too long (max 255 characters)")
    
    return location


def validate_description(description: Optional[str]) -> Optional[str]:
    """Validate event description"""
    if description is None:
        return None
    
    if not isinstance(description, str):
        raise ValidationException("Description must be a string")
    
    description = description.strip()
    
    if len(description) > 5000:
        raise ValidationException("Description is too long (max 5000 characters)")
    
    return description if description else None


def validate_date(event_date: date) -> date:
    """Validate event date"""
    if not isinstance(event_date, date):
        raise ValidationException("Event date must be a valid date")
    
    # Optionally, you can add business logic like preventing past dates
    # if event_date < date.today():
    #     raise ValidationException("Event date cannot be in the past")
    
    return event_date


def validate_time(event_time: time) -> time:
    """Validate event time"""
    if not isinstance(event_time, time):
        raise ValidationException("Event time must be a valid time")
    
    return event_time


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> None:
    """Validate date range"""
    if start_date and end_date:
        if start_date > end_date:
            raise ValidationException("Start date must be before or equal to end date")


def validate_role(role: Optional[str]) -> Optional[str]:
    """Validate user role"""
    if role is None:
        return None
    
    if not isinstance(role, str):
        raise ValidationException("Role must be a string")
    
    role = role.strip().lower()
    
    valid_roles = ['organizer', 'attendee']
    if role not in valid_roles:
        raise ValidationException(f"Role must be one of: {', '.join(valid_roles)}")
    
    return role


def validate_attendance_status(status: Optional[str]) -> Optional[str]:
    """Validate attendance status"""
    if status is None:
        return None
    
    if not isinstance(status, str):
        raise ValidationException("Attendance status must be a string")
    
    status = status.strip().lower()
    
    valid_statuses = ['pending', 'going', 'maybe', 'not_going']
    if status not in valid_statuses:
        raise ValidationException(f"Attendance status must be one of: {', '.join(valid_statuses)}")
    
    return status


def validate_user_id(user_id: int) -> int:
    """Validate user ID"""
    if not isinstance(user_id, int):
        raise ValidationException("User ID must be an integer")
    
    if user_id <= 0:
        raise ValidationException("User ID must be a positive integer")
    
    return user_id


def validate_event_id(event_id: int) -> int:
    """Validate event ID"""
    if not isinstance(event_id, int):
        raise ValidationException("Event ID must be an integer")
    
    if event_id <= 0:
        raise ValidationException("Event ID must be a positive integer")
    
    return event_id


def validate_keyword(keyword: Optional[str]) -> Optional[str]:
    """Validate search keyword"""
    if keyword is None:
        return None
    
    if not isinstance(keyword, str):
        raise ValidationException("Keyword must be a string")
    
    keyword = keyword.strip()
    
    if len(keyword) < 2:
        raise ValidationException("Keyword must be at least 2 characters long")
    
    if len(keyword) > 100:
        raise ValidationException("Keyword is too long (max 100 characters)")
    
    return keyword if keyword else None

