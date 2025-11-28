# Event Planner API Documentation

## Base URL
```
http://localhost:8000
```

## API Version
**Version:** 1.0.0

## Authentication
The API uses **no authentication** currently. User identification is done via `user_id` query parameters.

> **Note:** JWT tokens are generated on login but not currently enforced on protected routes.

## Response Format
All responses are in JSON format.

### Success Response
```json
{
  "data": {},
  "message": "Success message"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | OK - Request successful |
| 201  | Created - Resource created successfully |
| 204  | No Content - Request successful, no content to return |
| 400  | Bad Request - Invalid input |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource not found |
| 409  | Conflict - Resource already exists |
| 500  | Internal Server Error - Server error |

## Available Endpoints

### Authentication & Users
- [GET /me](./AUTH_ENDPOINTS.md#get-current-user) - Get current logged-in user
- [GET /users](./AUTH_ENDPOINTS.md#get-all-users) - Get all registered users
- [POST /signup](./AUTH_ENDPOINTS.md#signup) - Register new user
- [POST /login](./AUTH_ENDPOINTS.md#login) - User login

### Events
- [POST /events](./EVENT_ENDPOINTS.md#create-event) - Create new event
- [GET /events/organized](./EVENT_ENDPOINTS.md#get-organized-events) - Get user's organized events
- [GET /events/invited](./EVENT_ENDPOINTS.md#get-invited-events) - Get user's invited events
- [GET /events/invitations/sent](./EVENT_ENDPOINTS.md#get-my-invitations) - Get all people you invited and their status
- [GET /events/{event_id}/attendees](./EVENT_ENDPOINTS.md#get-event-attendees) - Get event attendees
- [POST /events/{event_id}/invite](./EVENT_ENDPOINTS.md#invite-user) - Invite user to event
- [PUT /events/{event_id}/attendance](./EVENT_ENDPOINTS.md#update-attendance-status) - Update attendance status
- [DELETE /events/{event_id}](./EVENT_ENDPOINTS.md#delete-event) - Delete event
- [GET /events/search](./EVENT_ENDPOINTS.md#search-events) - Advanced event search

### Health
- [GET /health](./HEALTH_ENDPOINTS.md) - Health check

## Interactive Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

