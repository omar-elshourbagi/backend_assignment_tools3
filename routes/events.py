from fastapi import APIRouter, HTTPException, status, Response, Query
from typing import List, Optional
from datetime import date as Date
from dto.schemas import EventCreateRequest, EventResponse, InviteRequest, Attendee, AttendanceStatusUpdate, InvitationInfo
from services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])
event_service = EventService()

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(request: EventCreateRequest, user_id: int = Query(..., description="User ID of the event creator")):
    try:
        event = event_service.create_event(
            user_id=user_id,
            title=request.title,
            date_value=request.date,
            time_value=request.time,
            location=request.location,
            description=request.description
        )
        # Coerce attendees to response model shape
        attendees = [Attendee(user_id=a["user_id"], role=a["role"], attendance_status=a.get("attendance_status", "pending")) for a in event.get("attendees", [])]
        return EventResponse(
            id=event["id"],
            title=event["title"],
            date=event["date"],
            time=event["time"],
            location=event["location"],
            description=event.get("description"),
            organizer_user_id=event["organizer_user_id"],
            attendees=attendees
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/organized", response_model=List[EventResponse])
def get_organized_events(user_id: int = Query(..., description="User ID to get organized events for")):
    events = event_service.get_organized_events(user_id)
    response: List[EventResponse] = []
    for e in events:
        attendees = [Attendee(user_id=a["user_id"], role=a["role"], attendance_status=a.get("attendance_status", "pending")) for a in e.get("attendees", [])]
        response.append(EventResponse(
            id=e["id"],
            title=e["title"],
            date=e["date"],
            time=e["time"],
            location=e["location"],
            description=e.get("description"),
            organizer_user_id=e["organizer_user_id"],
            attendees=attendees
        ))
    return response

@router.get("/invited", response_model=List[EventResponse])
def get_invited_events(user_id: int = Query(..., description="User ID to get invited events for")):
    events = event_service.get_invited_events(user_id)
    response: List[EventResponse] = []
    for e in events:
        attendees = [Attendee(user_id=a["user_id"], role=a["role"], attendance_status=a.get("attendance_status", "pending")) for a in e.get("attendees", [])]
        response.append(EventResponse(
            id=e["id"],
            title=e["title"],
            date=e["date"],
            time=e["time"],
            location=e["location"],
            description=e.get("description"),
            organizer_user_id=e["organizer_user_id"],
            attendees=attendees
        ))
    return response

@router.post("/{event_id}/invite", status_code=status.HTTP_201_CREATED)
def invite_user(event_id: int, body: InviteRequest, inviter_id: int = Query(..., description="User ID of the inviter")):
    try:
        result = event_service.invite_user(event_id=event_id, inviter_id=inviter_id, invited_user_id=body.userId)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, user_id: int = Query(..., description="User ID of the event owner")):
    try:
        event_service.delete_event(event_id=event_id, user_id=user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        # Event not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{event_id}/attendees", response_model=List[Attendee])
def get_event_attendees(event_id: int, user_id: int = Query(..., description="User ID (typically organizer)")):
    """Get list of all attendees and their statuses for a specific event"""
    try:
        attendees = event_service.get_event_attendees(event_id=event_id, requesting_user_id=user_id)
        return [Attendee(user_id=a["user_id"], role=a["role"], attendance_status=a.get("attendance_status", "pending")) for a in attendees]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{event_id}/attendance", status_code=status.HTTP_200_OK)
def update_attendance_status(event_id: int, body: AttendanceStatusUpdate, user_id: int = Query(..., description="User ID of the attendee")):
    """Update attendance status for an event (Going, Maybe, Not Going)"""
    try:
        result = event_service.update_attendance_status(event_id=event_id, user_id=user_id, status=body.status)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/search", response_model=List[EventResponse])
def search_events(
    user_id: int = Query(..., description="User ID performing the search"),
    keyword: Optional[str] = Query(None, description="Search keyword for event title or description"),
    start_date: Optional[Date] = Query(None, description="Start date for date range filter (YYYY-MM-DD)"),
    end_date: Optional[Date] = Query(None, description="End date for date range filter (YYYY-MM-DD)"),
    role: Optional[str] = Query(None, description="Filter by role: 'organizer' or 'attendee'"),
    location: Optional[str] = Query(None, description="Filter by location"),
    attendance_status: Optional[str] = Query(None, description="Filter by attendance status: 'pending', 'going', 'maybe', 'not_going'")
):
    """
    Advanced search for events with multiple filter options:
    - keyword: Search in event title and description
    - start_date/end_date: Filter by date range
    - role: Filter by user's role (organizer or attendee)
    - location: Filter by event location
    - attendance_status: Filter by user's attendance status
    """
    try:
        events = event_service.search_events(
            user_id=user_id,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            role=role,
            location=location,
            attendance_status=attendance_status
        )
        
        response: List[EventResponse] = []
        for e in events:
            attendees = [Attendee(user_id=a["user_id"], role=a["role"], attendance_status=a.get("attendance_status", "pending")) for a in e.get("attendees", [])]
            response.append(EventResponse(
                id=e["id"],
                title=e["title"],
                date=e["date"],
                time=e["time"],
                location=e["location"],
                description=e.get("description"),
                organizer_user_id=e["organizer_user_id"],
                attendees=attendees
            ))
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/invitations/sent", response_model=List[InvitationInfo])
def get_my_invitations(user_id: int = Query(..., description="Organizer's user ID")):
    """Get all people you have invited and their attendance status"""
    try:
        invitations = event_service.get_my_invitations(organizer_id=user_id)
        return [
            InvitationInfo(
                event_id=inv["event_id"],
                event_title=inv["event_title"],
                event_date=inv["event_date"],
                invited_user_id=inv["invited_user_id"],
                invited_user_name=inv["invited_user_name"],
                invited_user_email=inv["invited_user_email"],
                attendance_status=inv.get("attendance_status", "pending")
            )
            for inv in invitations
        ]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


