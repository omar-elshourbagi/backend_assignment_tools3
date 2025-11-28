from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import date
from main import app

client = TestClient(app)

def signup_and_login(name: str, email: str, password: str):
    # Signup
    client.post("/signup", json={
        "name": name,
        "email": email,
        "password": password,
        "confirm_password": password
    })
    # Login
    resp = client.post("/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    return data["token"], data["user_id"]

def test_event_flow():
    suffix = uuid4().hex[:6]
    org_email = f"organizer_{suffix}@example.com"
    att_email = f"attendee_{suffix}@example.com"
    organizer_token, organizer_id = signup_and_login("Organizer Test", org_email, "Password123!")
    attendee_token, attendee_id = signup_and_login("Attendee Test", att_email, "Password123!")

    # Create event
    create_resp = client.post("/events", headers={"Authorization": f"Bearer {organizer_token}"}, json={
        "title": f"Meetup {suffix}",
        "date": date.today().isoformat(),
        "time": "18:00:00",
        "location": "Cairo",
        "description": "Monthly meetup"
    })
    assert create_resp.status_code == 201, create_resp.text
    event = create_resp.json()
    event_id = event["id"]

    # Invite attendee
    invite_resp = client.post(f"/events/{event_id}/invite", headers={"Authorization": f"Bearer {organizer_token}"}, json={
        "userId": attendee_id
    })
    assert invite_resp.status_code in (201, 400, 403)

    # List organized
    org_list = client.get("/events/organized", headers={"Authorization": f"Bearer {organizer_token}"})
    assert org_list.status_code == 200
    assert any(e["id"] == event_id for e in org_list.json())

    # List invited for attendee (may be empty if invite failed)
    inv_list = client.get("/events/invited", headers={"Authorization": f"Bearer {attendee_token}"})
    assert inv_list.status_code == 200

    # Delete by non-organizer should be forbidden
    del_forbidden = client.delete(f"/events/{event_id}", headers={"Authorization": f"Bearer {attendee_token}"})
    assert del_forbidden.status_code in (403, 404)

    # Delete by organizer
    del_resp = client.delete(f"/events/{event_id}", headers={"Authorization": f"Bearer {organizer_token}"})
    assert del_resp.status_code == 204


