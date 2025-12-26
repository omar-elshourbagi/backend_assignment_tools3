from typing import Dict, Any, List, Optional
from datetime import date, time as time_type
import logging

from database import get_db_connection, close_db
from models.event_repository import MysqlEventRepository
from models.event_attendee_repository import MysqlEventAttendeeRepository
from models.user_repository import UserRepository
from handlers.exceptions import (
    NotFoundException,
    PermissionException,
    ValidationException,
    DatabaseException
)
from validators import (
    validate_title,
    validate_location,
    validate_description,
    validate_date,
    validate_time,
    validate_user_id,
    validate_event_id,
    validate_date_range,
    validate_role,
    validate_attendance_status,
    validate_keyword
)

logger = logging.getLogger(__name__)


class EventService:
    def __init__(
        self,
        event_repo: MysqlEventRepository = None,
        attendee_repo: MysqlEventAttendeeRepository = None
    ):
        self.event_repo = event_repo or MysqlEventRepository()
        self.attendee_repo = attendee_repo or MysqlEventAttendeeRepository()
        self.user_repo = UserRepository()

    def create_event(
        self,
        user_id: int,
        title: str,
        date_value: date,
        time_value: time_type,
        location: str,
        description: Optional[str]
    ) -> Dict[str, Any]:
        """Create event with validation and proper error handling"""

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

            self.attendee_repo.add_attendee(
                event_id=event["id"],
                user_id=user_id,
                role="organizer",
                conn=conn
            )

            conn.commit()

            event["attendees"] = [
                {
                    "user_id": user_id,
                    "role": "organizer",
                    "attendance_status": "pending"
                }
            ]

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

    def invite_user(
        self,
        event_id: int,
        inviter_id: int,
        invited_user_id: int
    ) -> Dict[str, Any]:

        event_id = validate_event_id(event_id)
        inviter_id = validate_user_id(inviter_id)
        invited_user_id = validate_user_id(invited_user_id)

        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))

        if not self.attendee_repo.is_user_organizer(event_id, inviter_id):
            raise PermissionException("Only organizer can invite users")

        invited_user = self.user_repo.get_user_by_id(invited_user_id)
        if not invited_user:
            raise NotFoundException("User", str(invited_user_id))

        if inviter_id == invited_user_id:
            raise ValidationException("Cannot invite yourself as an attendee")

        if self.attendee_repo.is_user_attendee(event_id, invited_user_id):
            raise ValidationException("User already invited to this event")

        attendee_id = self.attendee_repo.add_attendee(
            event_id,
            invited_user_id,
            "attendee"
        )

        logger.info(f"User {invited_user_id} invited to event {event_id}")
        return {
            "attendee_id": attendee_id,
            "event_id": event_id,
            "user_id": invited_user_id,
            "role": "attendee"
        }

    def delete_event(self, event_id: int, user_id: int) -> None:
        event_id = validate_event_id(event_id)
        user_id = validate_user_id(user_id)

        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))

        if event["organizer_user_id"] != user_id:
            raise PermissionException("Only organizer can delete the event")

        self.event_repo.delete_event(event_id)
        logger.info(f"Event {event_id} deleted by user {user_id}")

    def update_attendance_status(
        self,
        event_id: int,
        user_id: int,
        status: str
    ) -> Dict[str, Any]:

        event_id = validate_event_id(event_id)
        user_id = validate_user_id(user_id)
        status = validate_attendance_status(status)

        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))

        if not self.attendee_repo.is_user_attendee(event_id, user_id):
            raise ValidationException("User is not an attendee of this event")

        success = self.attendee_repo.update_attendance_status(
            event_id, user_id, status
        )
        if not success:
            raise DatabaseException("Failed to update attendance status")

        logger.info(
            f"Attendance updated for user {user_id} in event {event_id}"
        )
        return {
            "event_id": event_id,
            "user_id": user_id,
            "status": status
        }

    def get_event_attendees(
        self,
        event_id: int,
        requesting_user_id: int
    ) -> List[Dict[str, Any]]:

        event_id = validate_event_id(event_id)
        requesting_user_id = validate_user_id(requesting_user_id)

        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))

        is_organizer = self.attendee_repo.is_user_organizer(
            event_id, requesting_user_id
        )
        is_attendee = self.attendee_repo.is_user_attendee(
            event_id, requesting_user_id
        )

        if not (is_organizer or is_attendee):
            raise PermissionException(
                "You must be an organizer or attendee to view attendee list"
            )

        return self.attendee_repo.get_attendees(event_id)

    def search_events(
        self,
        user_id: int,
        keyword: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
        attendance_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        user_id = validate_user_id(user_id)
        keyword = validate_keyword(keyword) if keyword else None
        validate_date_range(start_date, end_date)
        role = validate_role(role) if role else None
        attendance_status = (
            validate_attendance_status(attendance_status)
            if attendance_status else None
        )

        if not self.user_repo.get_user_by_id(user_id):
            raise NotFoundException("User", str(user_id))

        events = self.event_repo.search_events(
            user_id=user_id,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            role=role,
            location=location,
            attendance_status=attendance_status
        )

        for event in events:
            event["attendees"] = self.attendee_repo.get_attendees(event["id"])

        return events

    def get_my_invitations(
        self,
        organizer_id: int
    ) -> List[Dict[str, Any]]:

        organizer_id = validate_user_id(organizer_id)

        if not self.user_repo.get_user_by_id(organizer_id):
            raise NotFoundException("User", str(organizer_id))

        return self.attendee_repo.get_my_invitations(organizer_id)
