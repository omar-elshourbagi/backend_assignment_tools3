# Event Management Endpoints

## Create Event

Create a new event. The creator automatically becomes the organizer.

### Endpoint
```
POST /events?user_id={user_id}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the user creating the event |

### Request Body
```json
{
  "title": "Team Meeting",
  "date": "2025-12-15",
  "time": "14:00:00",
  "location": "Cairo Office",
  "description": "Monthly team sync meeting"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Event title |
| date | string | Yes | Event date (YYYY-MM-DD format) |
| time | string | Yes | Event time (HH:MM:SS format) |
| location | string | Yes | Event location |
| description | string | No | Event description (optional) |

### Success Response (201 Created)
```json
{
  "id": 1,
  "title": "Team Meeting",
  "date": "2025-12-15",
  "time": "14:00:00",
  "location": "Cairo Office",
  "description": "Monthly team sync meeting",
  "organizer_user_id": 1,
  "attendees": [
    {
      "user_id": 1,
      "role": "organizer",
      "attendance_status": "pending"
    }
  ]
}
```

### Frontend Example
```javascript
const createEvent = async (eventData, userId) => {
  try {
    const response = await axios.post(
      `http://localhost:8000/events?user_id=${userId}`,
      {
        title: eventData.title,
        date: eventData.date,        // "2025-12-15"
        time: eventData.time,        // "14:00:00"
        location: eventData.location,
        description: eventData.description
      }
    );
    
    console.log('Event created:', response.data);
    return response.data;
  } catch (error) {
    alert(error.response?.data?.detail || 'Failed to create event');
    throw error;
  }
};
```

---

## Get Organized Events

Get all events organized by the user.

### Endpoint
```
GET /events/organized?user_id={user_id}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the user |

### Success Response (200 OK)
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "date": "2025-12-15",
    "time": "14:00:00",
    "location": "Cairo Office",
    "description": "Monthly team sync meeting",
    "organizer_user_id": 1,
    "attendees": [
      {
        "user_id": 1,
        "role": "organizer",
        "attendance_status": "pending"
      },
      {
        "user_id": 2,
        "role": "attendee",
        "attendance_status": "going"
      }
    ]
  }
]
```

### Frontend Example
```javascript
const getOrganizedEvents = async (userId) => {
  try {
    const response = await axios.get(
      `http://localhost:8000/events/organized?user_id=${userId}`
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch events:', error);
    throw error;
  }
};
```

---

## Get Invited Events

Get all events where the user is invited as an attendee.

### Endpoint
```
GET /events/invited?user_id={user_id}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the user |

### Success Response (200 OK)
```json
[
  {
    "id": 2,
    "title": "Project Kickoff",
    "date": "2025-12-20",
    "time": "10:00:00",
    "location": "Conference Room A",
    "description": "New project kickoff meeting",
    "organizer_user_id": 3,
    "attendees": [
      {
        "user_id": 3,
        "role": "organizer",
        "attendance_status": "pending"
      },
      {
        "user_id": 1,
        "role": "attendee",
        "attendance_status": "maybe"
      }
    ]
  }
]
```

### Frontend Example
```javascript
const getInvitedEvents = async (userId) => {
  try {
    const response = await axios.get(
      `http://localhost:8000/events/invited?user_id=${userId}`
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch invited events:', error);
    throw error;
  }
};
```

---

## Get My Invitations

Get all people you have invited across all your events with their attendance status.

### Endpoint
```
GET /events/invitations/sent?user_id={user_id}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the organizer |

### Success Response (200 OK)
```json
[
  {
    "event_id": 1,
    "event_title": "Team Meeting",
    "event_date": "2025-12-15",
    "invited_user_id": 2,
    "invited_user_name": "Jane Smith",
    "invited_user_email": "jane@example.com",
    "attendance_status": "going"
  },
  {
    "event_id": 1,
    "event_title": "Team Meeting",
    "event_date": "2025-12-15",
    "invited_user_id": 3,
    "invited_user_name": "Bob Johnson",
    "invited_user_email": "bob@example.com",
    "attendance_status": "pending"
  },
  {
    "event_id": 2,
    "event_title": "Project Review",
    "event_date": "2025-12-20",
    "invited_user_id": 2,
    "invited_user_name": "Jane Smith",
    "invited_user_email": "jane@example.com",
    "attendance_status": "maybe"
  }
]
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| event_id | integer | ID of the event |
| event_title | string | Title of the event |
| event_date | string | Date of the event (YYYY-MM-DD) |
| invited_user_id | integer | ID of the invited user |
| invited_user_name | string | Name of the invited user |
| invited_user_email | string | Email of the invited user |
| attendance_status | string | Status: "pending", "going", "maybe", "not_going" |

### Frontend Example
```javascript
const getMyInvitations = async (userId) => {
  try {
    const response = await axios.get(
      `http://localhost:8000/events/invitations/sent?user_id=${userId}`
    );
    
    // Group by status
    const invitations = response.data;
    const summary = {
      total: invitations.length,
      going: invitations.filter(i => i.attendance_status === 'going').length,
      maybe: invitations.filter(i => i.attendance_status === 'maybe').length,
      not_going: invitations.filter(i => i.attendance_status === 'not_going').length,
      pending: invitations.filter(i => i.attendance_status === 'pending').length
    };
    
    return { invitations, summary };
  } catch (error) {
    console.error('Failed to fetch invitations:', error);
    throw error;
  }
};
```

---

## Get Event Attendees

Get list of all attendees and their statuses for a specific event.

### Endpoint
```
GET /events/{event_id}/attendees?user_id={user_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| event_id | integer | ID of the event |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the requesting user (must be organizer or attendee) |

### Success Response (200 OK)
```json
[
  {
    "user_id": 1,
    "role": "organizer",
    "attendance_status": "pending"
  },
  {
    "user_id": 2,
    "role": "attendee",
    "attendance_status": "going"
  },
  {
    "user_id": 3,
    "role": "attendee",
    "attendance_status": "maybe"
  },
  {
    "user_id": 4,
    "role": "attendee",
    "attendance_status": "not_going"
  }
]
```

### Attendance Status Values

| Status | Description |
|--------|-------------|
| pending | No response yet (default) |
| going | Will attend |
| maybe | Might attend |
| not_going | Will not attend |

### Frontend Example
```javascript
const getEventAttendees = async (eventId, userId) => {
  try {
    const response = await axios.get(
      `http://localhost:8000/events/${eventId}/attendees?user_id=${userId}`
    );
    
    // Group attendees by status
    const attendeesByStatus = {
      going: response.data.filter(a => a.attendance_status === 'going'),
      maybe: response.data.filter(a => a.attendance_status === 'maybe'),
      not_going: response.data.filter(a => a.attendance_status === 'not_going'),
      pending: response.data.filter(a => a.attendance_status === 'pending')
    };
    
    return attendeesByStatus;
  } catch (error) {
    console.error('Failed to fetch attendees:', error);
    throw error;
  }
};
```

---

## Invite User

Invite a user to an event. Only the organizer can invite users.

### Endpoint
```
POST /events/{event_id}/invite?inviter_id={inviter_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| event_id | integer | ID of the event |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inviter_id | integer | Yes | ID of the organizer inviting the user |

### Request Body
```json
{
  "userId": 2
}
```

### Success Response (201 Created)
```json
{
  "attendee_id": 5,
  "event_id": 1,
  "user_id": 2,
  "role": "attendee"
}
```

### Error Responses

#### 403 Forbidden - Not organizer
```json
{
  "detail": "Only organizer can invite users"
}
```

#### 400 Bad Request - User already invited
```json
{
  "detail": "User already invited"
}
```

### Frontend Example
```javascript
const inviteUser = async (eventId, inviterId, userIdToInvite) => {
  try {
    const response = await axios.post(
      `http://localhost:8000/events/${eventId}/invite?inviter_id=${inviterId}`,
      {
        userId: userIdToInvite
      }
    );
    
    console.log('User invited:', response.data);
    return response.data;
  } catch (error) {
    if (error.response?.status === 403) {
      alert('Only the organizer can invite users');
    } else if (error.response?.status === 400) {
      alert('User is already invited');
    }
    throw error;
  }
};
```

---

## Update Attendance Status

Update the attendance status for an event (Going, Maybe, Not Going).

### Endpoint
```
PUT /events/{event_id}/attendance?user_id={user_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| event_id | integer | ID of the event |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the attendee updating their status |

### Request Body
```json
{
  "status": "going"
}
```

### Status Options
- `"pending"` - No response
- `"going"` - Will attend
- `"maybe"` - Might attend  
- `"not_going"` - Will not attend

### Success Response (200 OK)
```json
{
  "event_id": 1,
  "user_id": 2,
  "status": "going",
  "message": "Attendance status updated successfully"
}
```

### Error Responses

#### 400 Bad Request - Not an attendee
```json
{
  "detail": "User is not an attendee of this event"
}
```

### Frontend Example
```javascript
const updateAttendanceStatus = async (eventId, userId, status) => {
  try {
    const response = await axios.put(
      `http://localhost:8000/events/${eventId}/attendance?user_id=${userId}`,
      {
        status: status  // "going", "maybe", "not_going", "pending"
      }
    );
    
    console.log('Status updated:', response.data);
    return response.data;
  } catch (error) {
    alert(error.response?.data?.detail || 'Failed to update status');
    throw error;
  }
};

// React component example
const AttendanceButtons = ({ eventId, userId, currentStatus }) => {
  const handleStatusChange = async (newStatus) => {
    await updateAttendanceStatus(eventId, userId, newStatus);
    // Refresh event data
  };

  return (
    <div>
      <button 
        onClick={() => handleStatusChange('going')}
        className={currentStatus === 'going' ? 'active' : ''}
      >
        Going ✓
      </button>
      <button 
        onClick={() => handleStatusChange('maybe')}
        className={currentStatus === 'maybe' ? 'active' : ''}
      >
        Maybe ?
      </button>
      <button 
        onClick={() => handleStatusChange('not_going')}
        className={currentStatus === 'not_going' ? 'active' : ''}
      >
        Not Going ✗
      </button>
    </div>
  );
};
```

---

## Delete Event

Delete an event. Only the organizer can delete the event.

### Endpoint
```
DELETE /events/{event_id}?user_id={user_id}
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| event_id | integer | ID of the event to delete |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the organizer |

### Success Response (204 No Content)
No response body returned.

### Error Responses

#### 403 Forbidden - Not organizer
```json
{
  "detail": "Only organizer can delete the event"
}
```

#### 404 Not Found - Event doesn't exist
```json
{
  "detail": "Event not found"
}
```

### Frontend Example
```javascript
const deleteEvent = async (eventId, userId) => {
  if (!confirm('Are you sure you want to delete this event?')) {
    return;
  }

  try {
    await axios.delete(
      `http://localhost:8000/events/${eventId}?user_id=${userId}`
    );
    
    console.log('Event deleted successfully');
    // Redirect or refresh event list
  } catch (error) {
    if (error.response?.status === 403) {
      alert('Only the organizer can delete this event');
    } else if (error.response?.status === 404) {
      alert('Event not found');
    } else {
      alert('Failed to delete event');
    }
    throw error;
  }
};
```

---

## Search Events

Advanced search for events with multiple filter options.

### Endpoint
```
GET /events/search
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | ID of the user performing search |
| keyword | string | No | Search in event title and description |
| start_date | string | No | Start date for range filter (YYYY-MM-DD) |
| end_date | string | No | End date for range filter (YYYY-MM-DD) |
| role | string | No | Filter by role: "organizer" or "attendee" |
| location | string | No | Filter by location (partial match) |
| attendance_status | string | No | Filter by status: "pending", "going", "maybe", "not_going" |

### Example Queries

#### Search by keyword
```
GET /events/search?user_id=1&keyword=meeting
```

#### Search by date range
```
GET /events/search?user_id=1&start_date=2025-12-01&end_date=2025-12-31
```

#### Search organized events
```
GET /events/search?user_id=1&role=organizer
```

#### Search events user is going to
```
GET /events/search?user_id=1&role=attendee&attendance_status=going
```

#### Complex search
```
GET /events/search?user_id=1&keyword=team&location=Cairo&start_date=2025-12-01&role=organizer
```

### Success Response (200 OK)
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "date": "2025-12-15",
    "time": "14:00:00",
    "location": "Cairo Office",
    "description": "Monthly team sync meeting",
    "organizer_user_id": 1,
    "attendees": [...]
  }
]
```

### Frontend Example
```javascript
const searchEvents = async (userId, filters) => {
  try {
    const params = new URLSearchParams({ user_id: userId });
    
    if (filters.keyword) params.append('keyword', filters.keyword);
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);
    if (filters.role) params.append('role', filters.role);
    if (filters.location) params.append('location', filters.location);
    if (filters.status) params.append('attendance_status', filters.status);
    
    const response = await axios.get(
      `http://localhost:8000/events/search?${params.toString()}`
    );
    
    return response.data;
  } catch (error) {
    console.error('Search failed:', error);
    throw error;
  }
};

// Usage
const results = await searchEvents(1, {
  keyword: 'meeting',
  startDate: '2025-12-01',
  endDate: '2025-12-31',
  location: 'Cairo'
});
```

### React Search Component Example
```jsx
import { useState } from 'react';

const EventSearch = ({ userId }) => {
  const [filters, setFilters] = useState({
    keyword: '',
    startDate: '',
    endDate: '',
    role: '',
    location: '',
    status: ''
  });
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const params = new URLSearchParams({ user_id: userId });
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        const paramMap = {
          keyword: 'keyword',
          startDate: 'start_date',
          endDate: 'end_date',
          role: 'role',
          location: 'location',
          status: 'attendance_status'
        };
        params.append(paramMap[key], value);
      }
    });

    const response = await axios.get(
      `http://localhost:8000/events/search?${params.toString()}`
    );
    
    setResults(response.data);
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search keyword..."
        value={filters.keyword}
        onChange={(e) => setFilters({...filters, keyword: e.target.value})}
      />
      <input
        type="date"
        value={filters.startDate}
        onChange={(e) => setFilters({...filters, startDate: e.target.value})}
      />
      <input
        type="date"
        value={filters.endDate}
        onChange={(e) => setFilters({...filters, endDate: e.target.value})}
      />
      <select
        value={filters.role}
        onChange={(e) => setFilters({...filters, role: e.target.value})}
      >
        <option value="">All Roles</option>
        <option value="organizer">Organizer</option>
        <option value="attendee">Attendee</option>
      </select>
      <button onClick={handleSearch}>Search</button>

      <div>
        {results.map(event => (
          <div key={event.id}>
            <h3>{event.title}</h3>
            <p>{event.date} at {event.time}</p>
            <p>{event.location}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

