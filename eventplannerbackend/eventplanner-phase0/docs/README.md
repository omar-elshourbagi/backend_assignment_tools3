# Event Planner API Documentation 📚

Complete API documentation for frontend integration.

## 📖 Table of Contents

1. **[API Overview](./API_OVERVIEW.md)** - Start here!
   - Base URL and general information
   - Response formats
   - HTTP status codes
   - List of all endpoints

2. **[Authentication Endpoints](./AUTH_ENDPOINTS.md)**
   - User signup
   - User login
   - Complete with examples

3. **[Event Endpoints](./EVENT_ENDPOINTS.md)**
   - Create event
   - Get organized/invited events
   - Invite users
   - Update attendance status
   - Delete event
   - Advanced search

4. **[Health Check](./HEALTH_ENDPOINTS.md)**
   - API health status

5. **[Data Models](./DATA_MODELS.md)**
   - User model
   - Event model
   - Attendee model
   - TypeScript definitions
   - React context examples

6. **[Frontend Integration Guide](./FRONTEND_INTEGRATION.md)**
   - Quick start
   - Axios setup
   - Service layer examples
   - Common integration patterns
   - Error handling
   - Testing

7. **[Postman Collection](./POSTMAN_COLLECTION.md)**
   - All endpoints ready for Postman
   - Request/Response examples
   - Environment variables

8. **[Postman Import File](./EventPlanner.postman_collection.json)**
   - Import directly into Postman

## 🚀 Quick Start for Frontend Developers

### Step 1: Start the API
```bash
# Backend should be running on:
http://localhost:8000
```

### Step 2: Test the API
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Step 3: View Interactive Docs
Open in browser:
```
http://localhost:8000/docs
```

### Step 4: Install Axios in Your Frontend
```bash
npm install axios
```

### Step 5: Copy Service Files
Use the examples from [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) to create:
- `src/api/client.js` - Axios instance
- `src/api/authService.js` - Auth methods
- `src/api/eventService.js` - Event methods

### Step 6: Implement Login Flow
```javascript
import { authService } from './api/authService';

// Login
const user = await authService.login(email, password);
// user_id is now stored in localStorage

// Use user_id for all subsequent API calls
const userId = authService.getCurrentUserId();
```

## 📋 Common Workflows

### User Authentication
```
1. User fills signup form
2. POST /signup → Get user_id
3. Store user_id in localStorage
4. Redirect to dashboard
```

### Creating an Event
```
1. Get user_id from localStorage
2. User fills event form
3. POST /events?user_id={id}
4. Event created with user as organizer
```

### Viewing Events
```
1. Get user_id from localStorage
2. GET /events/organized?user_id={id} (events user created)
3. GET /events/invited?user_id={id} (events user is invited to)
4. Display both lists
```

### Responding to Event Invitation
```
1. User clicks "Going" button
2. PUT /events/{event_id}/attendance?user_id={id}
3. Body: { "status": "going" }
4. Status updated, refresh UI
```

### Searching Events
```
1. User enters search criteria
2. Build query string with filters
3. GET /events/search?user_id={id}&keyword=...&date=...
4. Display filtered results
```

## 🎯 Key Points for Frontend

### User ID is Required
- Store `user_id` after login in localStorage
- Pass it as query parameter in all API calls
- Example: `?user_id=1`

### No Token Validation (Currently)
- JWT tokens are generated but not enforced
- User identification is via `user_id` parameter
- This may change in future versions

### Date/Time Format
- **Date**: `YYYY-MM-DD` (e.g., "2025-12-15")
- **Time**: `HH:MM:SS` (e.g., "14:00:00")
- Use HTML5 date/time inputs for proper formatting

### Attendance Status Values
- `"pending"` - Default, no response
- `"going"` - User will attend
- `"maybe"` - User might attend
- `"not_going"` - User won't attend

### Role-Based Permissions
- **Organizer**: Can invite users, delete event
- **Attendee**: Can update own attendance status

## 🔧 Environment Setup

### Development
```javascript
const API_URL = 'http://localhost:8000';
```

### Production (Future)
```javascript
const API_URL = 'https://api.yourapp.com';
```

## 📝 Response Structure

### Success Response Example
```json
{
  "id": 1,
  "title": "Event Title",
  "date": "2025-12-15",
  ...
}
```

### Error Response Example
```json
{
  "detail": "Error message here"
}
```

## 🐛 Common Issues & Solutions

### Issue: CORS Error
**Solution**: Make sure API is running and allows requests from your frontend origin.

### Issue: 401 Unauthorized
**Solution**: Check that `user_id` is correctly passed as query parameter.

### Issue: 404 Not Found
**Solution**: Verify endpoint URL and path parameters (e.g., `event_id`).

### Issue: 400 Bad Request
**Solution**: Check request body format matches expected schema.

## 📞 Need Help?

1. Check the [API Overview](./API_OVERVIEW.md) first
2. Look at specific endpoint documentation
3. Try examples in [Frontend Integration Guide](./FRONTEND_INTEGRATION.md)
4. Test endpoints in Swagger UI: `http://localhost:8000/docs`

## 📚 Additional Resources

- **Swagger UI**: `http://localhost:8000/docs` - Interactive API testing
- **OpenAPI Spec**: `http://localhost:8000/openapi.json` - API specification
- **TypeScript Types**: See [DATA_MODELS.md](./DATA_MODELS.md)

---

**Last Updated**: November 2025  
**API Version**: 1.0.0

