import pytest
from services.event_service import EventService

class StubEventRepo:
    def __init__(self, organizer_id: int):
        self.organizer_id = organizer_id
        self.deleted = False
    def get_event_by_id(self, event_id: int):
        return {"id": event_id, "organizer_user_id": self.organizer_id}
    def delete_event(self, event_id: int, conn=None):
        self.deleted = True

class StubAttendeeRepo:
    pass

def test_delete_event_permission():
    stub_repo = StubEventRepo(organizer_id=1)
    service = EventService(event_repo=stub_repo, attendee_repo=StubAttendeeRepo())
    # Non-organizer cannot delete
    with pytest.raises(PermissionError):
        service.delete_event(event_id=10, user_id=2)
    # Organizer can delete
    service.delete_event(event_id=10, user_id=1)
    assert stub_repo.deleted is True


