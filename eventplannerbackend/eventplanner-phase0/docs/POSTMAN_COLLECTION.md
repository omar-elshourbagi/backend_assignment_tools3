# Postman Collection - Event Planner API

## Base URL
```
http://localhost:8000
```

---

## 🔐 Authentication Endpoints

### 1. Get Current User (Who is Logged In)
```
GET {{base_url}}/me?user_id=1
```

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | The logged-in user's ID |

**Response Example:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

### 2. Get All Users
```
GET {{base_url}}/users
```

**Headers:**
```
Content-Type: application/json
```

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
]
```

---

### 2. Sign Up
```
POST {{base_url}}/signup
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response Example:**
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

---

### 3. Login
```
POST {{base_url}}/login
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response Example:**
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

---

## 📅 Event Endpoints

### 4. Create Event
```
POST {{base_url}}/events?user_id=1
```

**Headers:**
```
Content-Type: application/json
```

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | ID of the user creating the event |

**Body (raw JSON):**
```json
{
  "title": "Team Meeting",
  "date": "2025-12-15",
  "time": "14:00:00",
  "location": "Cairo Office",
  "description": "Monthly team sync"
}
```

**Response Example:**
```json
{
  "id": 1,
  "title": "Team Meeting",
  "date": "2025-12-15",
  "time": "14:00:00",
  "location": "Cairo Office",
  "description": "Monthly team sync",
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

---

### 5. Get Organized Events
```
GET {{base_url}}/events/organized?user_id=1
```

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | ID of the user |

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "date": "2025-12-15",
    "time": "14:00:00",
    "location": "Cairo Office",
    "description": "Monthly team sync",
    "organizer_user_id": 1,
    "attendees": [...]
  }
]
```

---

### 6. Get Invited Events
```
GET {{base_url}}/events/invited?user_id=2
```

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 2 | ID of the user |

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "date": "2025-12-15",
    "time": "14:00:00",
    "location": "Cairo Office",
    "description": "Monthly team sync",
    "organizer_user_id": 1,
    "attendees": [...]
  }
]
```

---

### 7. Get My Invitations (Who I Invited)
```
GET {{base_url}}/events/invitations/sent?user_id=1
```

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | ID of the organizer |

**Response Example:**
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
  }
]
```

---

### 8. Get Event Attendees (renumber remaining)
```
GET {{base_url}}/events/1/attendees?user_id=1
```

**Path Variables:**
| Key | Value | Description |
|-----|-------|-------------|
| event_id | 1 | ID of the event |

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | ID of the requesting user |

**Response Example:**
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
  }
]
```

---

### 8. Invite User to Event
```
POST {{base_url}}/events/1/invite?inviter_id=1
```

**Path Variables:**
| Key | Value | Description |
|-----|-------|-------------|
| event_id | 1 | ID of the event |

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| inviter_id | 1 | ID of the organizer inviting |

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "userId": 2
}
```

⚠️ **Note:** The field is `userId` (camelCase), NOT `user_id`!

**Response Example:**
```json
{
  "attendee_id": 5,
  "event_id": 1,
  "user_id": 2,
  "role": "attendee"
}
```

---

### 9. Update Attendance Status
```
PUT {{base_url}}/events/1/attendance?user_id=2
```

**Path Variables:**
| Key | Value | Description |
|-----|-------|-------------|
| event_id | 1 | ID of the event |

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 2 | ID of the attendee |

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "status": "going"
}
```

**Status Options:**
- `"pending"` - No response
- `"going"` - Will attend
- `"maybe"` - Might attend
- `"not_going"` - Will not attend

**Response Example:**
```json
{
  "event_id": 1,
  "user_id": 2,
  "status": "going",
  "message": "Attendance status updated successfully"
}
```

---

### 10. Delete Event
```
DELETE {{base_url}}/events/1?user_id=1
```

**Path Variables:**
| Key | Value | Description |
|-----|-------|-------------|
| event_id | 1 | ID of the event to delete |

**Query Params:**
| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | ID of the organizer |

**Response:** 204 No Content (empty body)

---

### 11. Search Events
```
GET {{base_url}}/events/search?user_id=1&keyword=meeting&start_date=2025-12-01&end_date=2025-12-31
```

**Query Params:**
| Key | Value | Required | Description |
|-----|-------|----------|-------------|
| user_id | 1 | ✅ Yes | ID of the user |
| keyword | meeting | No | Search in title/description |
| start_date | 2025-12-01 | No | Start date (YYYY-MM-DD) |
| end_date | 2025-12-31 | No | End date (YYYY-MM-DD) |
| role | organizer | No | Filter: "organizer" or "attendee" |
| location | Cairo | No | Filter by location |
| attendance_status | going | No | Filter: "pending", "going", "maybe", "not_going" |

**Response Example:**
```json
[
  {
    "id": 1,
    "title": "Team Meeting",
    "date": "2025-12-15",
    "time": "14:00:00",
    "location": "Cairo Office",
    "description": "Monthly team sync",
    "organizer_user_id": 1,
    "attendees": [...]
  }
]
```

---

## 🏥 Health Check

### 12. Health Check
```
GET {{base_url}}/health
```

**Response Example:**
```json
{
  "status": "ok"
}
```

---

## 📋 Postman Environment Variables

Create a Postman Environment with these variables:

| Variable | Initial Value | Description |
|----------|---------------|-------------|
| base_url | http://localhost:8000 | API base URL |
| user_id | 1 | Current logged-in user ID |
| event_id | 1 | Current event ID |

---

## 🚀 Quick Test Flow

1. **Health Check** - Verify API is running
2. **Sign Up** - Create user 1 (organizer)
3. **Sign Up** - Create user 2 (attendee)
4. **Login** - Login as user 1, note the `user_id`
5. **Create Event** - Create event with user 1
6. **Invite User** - Invite user 2 to the event
7. **Update Attendance** - User 2 responds "going"
8. **Get Attendees** - View all attendees with statuses
9. **Search Events** - Search for the event
10. **Delete Event** - Delete the event (organizer only)

