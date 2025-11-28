# Data Models

## User

Represents a user in the system.

```typescript
interface User {
  user_id: number;      // Unique user identifier
  name: string;         // User's full name
  email: string;        // User's email (unique)
}
```

### Example
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

## Event

Represents an event with all details and attendees.

```typescript
interface Event {
  id: number;                    // Unique event identifier
  title: string;                 // Event title
  date: string;                  // Event date (YYYY-MM-DD)
  time: string;                  // Event time (HH:MM:SS)
  location: string;              // Event location
  description: string | null;    // Event description (optional)
  organizer_user_id: number;     // ID of the user who created the event
  attendees: Attendee[];         // List of attendees
}
```

### Example
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
    },
    {
      "user_id": 2,
      "role": "attendee",
      "attendance_status": "going"
    }
  ]
}
```

---

## Attendee

Represents an attendee's participation in an event.

```typescript
interface Attendee {
  user_id: number;                          // User ID
  role: 'organizer' | 'attendee';           // User's role in the event
  attendance_status: AttendanceStatus;      // User's attendance status
}

type AttendanceStatus = 'pending' | 'going' | 'maybe' | 'not_going';
```

### Role Values

| Role | Description |
|------|-------------|
| organizer | Event creator (can invite users, delete event) |
| attendee | Invited participant |

### Attendance Status Values

| Status | Description | Icon Suggestion |
|--------|-------------|-----------------|
| pending | No response yet (default) | ⏳ |
| going | Will attend | ✓ |
| maybe | Might attend | ? |
| not_going | Will not attend | ✗ |

### Example
```json
{
  "user_id": 2,
  "role": "attendee",
  "attendance_status": "going"
}
```

---

## TypeScript Definitions

Complete TypeScript definitions for frontend use:

```typescript
// User Types
export interface User {
  user_id: number;
  name: string;
  email: string;
}

export interface SignUpData {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface LoginResponse {
  user_id: number;
  name: string;
  email: string;
  token: string;
  message: string;
}

// Event Types
export type AttendanceStatus = 'pending' | 'going' | 'maybe' | 'not_going';
export type Role = 'organizer' | 'attendee';

export interface Attendee {
  user_id: number;
  role: Role;
  attendance_status: AttendanceStatus;
}

export interface Event {
  id: number;
  title: string;
  date: string;  // YYYY-MM-DD
  time: string;  // HH:MM:SS
  location: string;
  description: string | null;
  organizer_user_id: number;
  attendees: Attendee[];
}

export interface CreateEventData {
  title: string;
  date: string;  // YYYY-MM-DD
  time: string;  // HH:MM:SS
  location: string;
  description?: string;
}

export interface SearchFilters {
  keyword?: string;
  start_date?: string;  // YYYY-MM-DD
  end_date?: string;    // YYYY-MM-DD
  role?: Role;
  location?: string;
  attendance_status?: AttendanceStatus;
}

// API Response Types
export interface ApiError {
  detail: string;
}

export interface HealthResponse {
  status: string;
}
```

---

## Frontend State Management Example

### React Context Example

```typescript
// EventContext.tsx
import { createContext, useContext, useState } from 'react';

interface EventContextType {
  events: Event[];
  loading: boolean;
  error: string | null;
  fetchOrganizedEvents: (userId: number) => Promise<void>;
  fetchInvitedEvents: (userId: number) => Promise<void>;
  createEvent: (userId: number, eventData: CreateEventData) => Promise<Event>;
  deleteEvent: (eventId: number, userId: number) => Promise<void>;
  updateAttendance: (eventId: number, userId: number, status: AttendanceStatus) => Promise<void>;
}

const EventContext = createContext<EventContextType | undefined>(undefined);

export const EventProvider: React.FC = ({ children }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOrganizedEvents = async (userId: number) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/events/organized?user_id=${userId}`
      );
      setEvents(response.data);
    } catch (err) {
      setError('Failed to fetch events');
    } finally {
      setLoading(false);
    }
  };

  const createEvent = async (userId: number, eventData: CreateEventData) => {
    const response = await axios.post(
      `http://localhost:8000/events?user_id=${userId}`,
      eventData
    );
    setEvents([...events, response.data]);
    return response.data;
  };

  // ... other methods

  return (
    <EventContext.Provider value={{
      events,
      loading,
      error,
      fetchOrganizedEvents,
      fetchInvitedEvents,
      createEvent,
      deleteEvent,
      updateAttendance
    }}>
      {children}
    </EventContext.Provider>
  );
};

export const useEvents = () => {
  const context = useContext(EventContext);
  if (!context) {
    throw new Error('useEvents must be used within EventProvider');
  }
  return context;
};
```

### Usage in Component

```typescript
const MyEventsPage = () => {
  const { events, loading, fetchOrganizedEvents } = useEvents();
  const userId = localStorage.getItem('user_id');

  useEffect(() => {
    if (userId) {
      fetchOrganizedEvents(parseInt(userId));
    }
  }, [userId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {events.map(event => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
};
```

