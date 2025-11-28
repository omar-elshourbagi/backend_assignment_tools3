from typing import Protocol, List, Optional, Dict, Any
from datetime import date, time as time_type

class IEventRepository(Protocol):
    def create_event(self, organizer_user_id: int, title: str, date_value: date, time_value: time_type, location: str, description: Optional[str], conn=None) -> Dict[str, Any]:
        ...

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        ...

    def get_events_by_organizer(self, user_id: int) -> List[Dict[str, Any]]:
        ...

    def delete_event(self, event_id: int, conn=None) -> None:
        ...

class IEventAttendeeRepository(Protocol):
    def add_attendee(self, event_id: int, user_id: int, role: str, conn=None) -> int:
        ...

    def get_attendees(self, event_id: int) -> List[Dict[str, Any]]:
        ...

    def is_user_organizer(self, event_id: int, user_id: int) -> bool:
        ...

    def is_user_attendee(self, event_id: int, user_id: int) -> bool:
        ...

    def get_invited_events_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        ...


