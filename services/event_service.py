from typing import Dict, Any, List, Optional
from datetime import date, time as time_type
import mysql.connector
from database import get_db_connection, close_db
from models.event_repository import MysqlEventRepository
from models.event_attendee_repository import MysqlEventAttendeeRepository
from models.user_repository import UserRepository
from config import DB_CONFIG

class EventService:
    def __init__(self, event_repo: MysqlEventRepository = None, attendee_repo: MysqlEventAttendeeRepository = None):
        self.event_repo = event_repo or MysqlEventRepository()
        self.attendee_repo = attendee_repo or MysqlEventAttendeeRepository()
        self.user_repo = UserRepository()

    def create_event(self, user_id: int, title: str, date_value: date, time_value: time_type, location: str, description: str | None) -> Dict[str, Any]:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")
        conn.start_transaction()
        try:
            # Ensure user exists
            if not self.user_repo.get_user_by_id(user_id):
                raise ValueError("Organizer user does not exist")
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
            return event
        except Exception:
            conn.rollback()
            raise
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
        # Validate inviter is organizer
        if not self.attendee_repo.is_user_organizer(event_id, inviter_id):
            raise PermissionError("Only organizer can invite users")
        # Validate invited user exists
        if not self.user_repo.get_user_by_id(invited_user_id):
            raise ValueError("Invited user does not exist")
        # Prevent duplicates
        if self.attendee_repo.is_user_attendee(event_id, invited_user_id):
            raise ValueError("User already invited")
        attendee_id = self.attendee_repo.add_attendee(event_id, invited_user_id, "attendee")
        return {"attendee_id": attendee_id, "event_id": event_id, "user_id": invited_user_id, "role": "attendee"}

    def delete_event(self, event_id: int, user_id: int) -> None:
        # Ensure event exists and user is organizer
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if event["organizer_user_id"] != user_id:
            raise PermissionError("Only organizer can delete the event")
        # Deletion will cascade attendees
        self.event_repo.delete_event(event_id)

    def update_attendance_status(self, event_id: int, user_id: int, status: str) -> Dict[str, Any]:
        """Update attendance status for an attendee"""
        # Validate event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        # Validate user is an attendee
        if not self.attendee_repo.is_user_attendee(event_id, user_id):
            raise ValueError("User is not an attendee of this event")
        # Update status
        success = self.attendee_repo.update_attendance_status(event_id, user_id, status)
        if not success:
            raise ValueError("Failed to update attendance status")
        return {"event_id": event_id, "user_id": user_id, "status": status, "message": "Attendance status updated successfully"}

    def get_event_attendees(self, event_id: int, requesting_user_id: int) -> List[Dict[str, Any]]:
        """Get all attendees and their statuses for an event. Organizer can view all statuses."""
        # Validate event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        # Check if requesting user is the organizer or an attendee
        is_organizer = self.attendee_repo.is_user_organizer(event_id, requesting_user_id)
        is_attendee = self.attendee_repo.is_user_attendee(event_id, requesting_user_id)
        
        if not (is_organizer or is_attendee):
            raise PermissionError("You must be an organizer or attendee to view attendee list")
        
        # Get all attendees with their statuses
        return self.attendee_repo.get_attendees(event_id)

    def search_events(self, user_id: int, keyword: Optional[str] = None,
                     start_date: Optional[date] = None, end_date: Optional[date] = None,
                     role: Optional[str] = None, location: Optional[str] = None,
                     attendance_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Advanced search for events with multiple filter options"""
        # Validate user exists
        if not self.user_repo.get_user_by_id(user_id):
            raise ValueError("User does not exist")
        
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
        # Validate user exists
        if not self.user_repo.get_user_by_id(organizer_id):
            raise ValueError("User does not exist")
        
        return self.attendee_repo.get_my_invitations(organizer_id)


