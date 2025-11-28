from typing import Dict, Any, List, Optional
from datetime import date, time as time_type
import mysql.connector
import logging
from database import get_db_connection, close_db
from models.event_repository import MysqlEventRepository
from models.event_attendee_repository import MysqlEventAttendeeRepository
from models.user_repository import UserRepository
from config import DB_CONFIG
from handlers.exceptions import NotFoundException, PermissionException, ValidationException, DatabaseException
from validators import (
    validate_title, validate_location, validate_description, validate_date, validate_time,
    validate_user_id, validate_event_id, validate_date_range, validate_role, validate_attendance_status
)

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self, event_repo: MysqlEventRepository = None, attendee_repo: MysqlEventAttendeeRepository = None):
        self.event_repo = event_repo or MysqlEventRepository()
        self.attendee_repo = attendee_repo or MysqlEventAttendeeRepository()
        self.user_repo = UserRepository()

    def create_event(self, user_id: int, title: str, date_value: date, time_value: time_type, location: str, description: str | None) -> Dict[str, Any]:
        """Create event with validation and proper error handling"""
        # Validate inputs
        user_id = validate_user_id(user_id)
        title = validate_title(title)
        location = validate_location(location)
        description = validate_description(description)
        date_value = validate_date(date_value)
        time_value = validate_time(time_value)
        
        conn = None
        try:
            conn = get_db_connection()
            conn.start_transaction()
            
            # Ensure user exists
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User", str(user_id))
            
            event = self.event_repo.create_event(
                organizer_user_id=user_id,
                title=title,
                date_value=date_value,
                time_value=time_value,
                location=location,
                description=description,
                conn=conn
            )
            # Mark creator as organizer
            self.attendee_repo.add_attendee(event_id=event["id"], user_id=user_id, role="organizer", conn=conn)
            conn.commit()
            event["attendees"] = [{"user_id": user_id, "role": "organizer", "attendance_status": "pending"}]
            logger.info(f"Event created successfully: {event['id']}")
            return event
        except (NotFoundException, ValidationException, PermissionException):
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error creating event: {str(e)}")
            raise DatabaseException("Failed to create event")
        finally:
            close_db(conn)

    def get_organized_events(self, user_id: int) -> List[Dict[str, Any]]:
        events = self.event_repo.get_events_by_organizer(user_id)
        for event in events:
            event["attendees"] = self.attendee_repo.get_attendees(event["id"])
        return events

    def get_invited_events(self, user_id: int) -> List[Dict[str, Any]]:
        events = self.attendee_repo.get_invited_events_for_user(user_id)
        for event in events:
            event["attendees"] = self.attendee_repo.get_attendees(event["id"])
        return events

    def invite_user(self, event_id: int, inviter_id: int, invited_user_id: int) -> Dict[str, Any]:
        """Invite user to event with validation and proper error handling"""
        # Validate inputs
        event_id = validate_event_id(event_id)
        inviter_id = validate_user_id(inviter_id)
        invited_user_id = validate_user_id(invited_user_id)
        
        # Validate event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))
        
        # Validate inviter is organizer
        if not self.attendee_repo.is_user_organizer(event_id, inviter_id):
            raise PermissionException("Only organizer can invite users")
        
        # Validate invited user exists
        invited_user = self.user_repo.get_user_by_id(invited_user_id)
        if not invited_user:
            raise NotFoundException("User", str(invited_user_id))
        
        # Prevent self-invitation as attendee (organizer is already added)
        if inviter_id == invited_user_id:
            raise ValidationException("Cannot invite yourself as an attendee")
        
        # Prevent duplicates
        if self.attendee_repo.is_user_attendee(event_id, invited_user_id):
            raise ValidationException("User already invited to this event")
        
        attendee_id = self.attendee_repo.add_attendee(event_id, invited_user_id, "attendee")
        logger.info(f"User {invited_user_id} invited to event {event_id}")
        return {"attendee_id": attendee_id, "event_id": event_id, "user_id": invited_user_id, "role": "attendee"}

    def delete_event(self, event_id: int, user_id: int) -> None:
        """Delete event with validation and proper error handling"""
        # Validate inputs
        event_id = validate_event_id(event_id)
        user_id = validate_user_id(user_id)
        
        # Ensure event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))
        
        # Ensure user is organizer
        if event["organizer_user_id"] != user_id:
            raise PermissionException("Only organizer can delete the event")
        
        # Deletion will cascade attendees
        self.event_repo.delete_event(event_id)
        logger.info(f"Event {event_id} deleted by user {user_id}")

    def update_attendance_status(self, event_id: int, user_id: int, status: str) -> Dict[str, Any]:
        """Update attendance status for an attendee with validation"""
        # Validate inputs
        event_id = validate_event_id(event_id)
        user_id = validate_user_id(user_id)
        status = validate_attendance_status(status)
        
        # Validate event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))
        
        # Validate user is an attendee
        if not self.attendee_repo.is_user_attendee(event_id, user_id):
            raise ValidationException("User is not an attendee of this event")
        
        # Update status
        success = self.attendee_repo.update_attendance_status(event_id, user_id, status)
        if not success:
            raise DatabaseException("Failed to update attendance status")
        
        logger.info(f"Attendance status updated for user {user_id} in event {event_id} to {status}")
        return {"event_id": event_id, "user_id": user_id, "status": status, "message": "Attendance status updated successfully"}

    def get_event_attendees(self, event_id: int, requesting_user_id: int) -> List[Dict[str, Any]]:
        """Get all attendees and their statuses for an event with validation"""
        # Validate inputs
        event_id = validate_event_id(event_id)
        requesting_user_id = validate_user_id(requesting_user_id)
        
        # Validate event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))
        
        # Check if requesting user is the organizer or an attendee
        is_organizer = self.attendee_repo.is_user_organizer(event_id, requesting_user_id)
        is_attendee = self.attendee_repo.is_user_attendee(event_id, requesting_user_id)
        
        if not (is_organizer or is_attendee):
            raise PermissionException("You must be an organizer or attendee to view attendee list")
        
        # Get all attendees with their statuses
        return self.attendee_repo.get_attendees(event_id)

    def search_events(self, user_id: int, keyword: Optional[str] = None,
                     start_date: Optional[date] = None, end_date: Optional[date] = None,
                     role: Optional[str] = None, location: Optional[str] = None,
                     attendance_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Advanced search for events with validation"""
        # Validate inputs
        user_id = validate_user_id(user_id)
        keyword = validate_keyword(keyword) if keyword else None
        validate_date_range(start_date, end_date)
        role = validate_role(role) if role else None
        attendance_status = validate_attendance_status(attendance_status) if attendance_status else None
        
        # Validate user exists
        if not self.user_repo.get_user_by_id(user_id):
            raise NotFoundException("User", str(user_id))
        
        # Perform search
        events = self.event_repo.search_events(
            user_id=user_id,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            role=role,
            location=location,
            attendance_status=attendance_status
        )
        
        # Attach attendees to each event
        for event in events:
            event["attendees"] = self.attendee_repo.get_attendees(event["id"])
        
        return events

    def get_my_invitations(self, organizer_id: int) -> List[Dict[str, Any]]:
        """Get all people the organizer has invited with their status"""
        # Validate inputs
        organizer_id = validate_user_id(organizer_id)
        
        # Validate user exists
        if not self.user_repo.get_user_by_id(organizer_id):
            raise NotFoundException("User", str(organizer_id))
        
        return self.attendee_repo.get_my_invitations(organizer_id)


