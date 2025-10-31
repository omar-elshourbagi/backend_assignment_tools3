# EventPlanner - Phase 0: User Management

This is the Phase 0 implementation of the EventPlanner system, focusing on User Management (Sign up and Login) built with FastAPI.

## Features

- **User Registration (Sign Up)**: Users can create an account with email and password
- **User Login**: Users can authenticate with their credentials
- **Input Validation**: Email format and password strength validation using Pydantic
- **Password Security**: Passwords are hashed using bcrypt via passlib
- **Swagger UI**: Interactive API documentation for testing endpoints
- **Error Handling**: Comprehensive error messages for various scenarios
- **Modular Architecture**: Clean separation of concerns for easy feature addition

## Tech Stack

- **Backend**: FastAPI (modern Python web framework)
- **Database**: SQLite
- **Security**: Passlib with bcrypt for password hashing
- **API Documentation**: Swagger/OpenAPI (built-in with FastAPI)
- **Validation**: Pydantic for request/response validation

## Project Structure

\`\`\`
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and initialization
├── schemas.py             # Pydantic models for validation
├── utils.py               # Utility functions (hashing, validation)
├── services/
│   └── auth_service.py    # Business logic for authentication
├── routes/
│   ├── auth.py            # Authentication endpoints
│   └── health.py          # Health check endpoints
├── requirements.txt       # Python dependencies
└── README.md             # This file
\`\`\`

## Installation

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Run the FastAPI application:
\`\`\`bash
python main.py
\`\`\`

The server will start on `http://localhost:8000`

## Swagger UI

Access the interactive API documentation at:
\`\`\`
http://localhost:8000/api/docs
\`\`\`

You can test all endpoints directly from the Swagger UI interface.

## API Endpoints

### Sign Up
- **Endpoint**: `POST /api/auth/signup`
- **Description**: Register a new user with email and password
- **Request Body**:
\`\`\`json
{
  "email": "user@example.com",
  "password": "password123"
}
\`\`\`
- **Success Response** (201):
\`\`\`json
{
  "user_id": 1,
  "email": "user@example.com",
  "message": "User registered successfully"
}
\`\`\`
- **Error Responses**:
  - 400: Invalid email format or weak password
  - 409: Email already registered
  - 500: Server error

### Login
- **Endpoint**: `POST /api/auth/login`
- **Description**: Authenticate user with email and password
- **Request Body**:
\`\`\`json
{
  "email": "user@example.com",
  "password": "password123"
}
\`\`\`
- **Success Response** (200):
\`\`\`json
{
  "user_id": 1,
  "email": "user@example.com",
  "message": "Login successful"
}
\`\`\`
- **Error Responses**:
  - 400: Missing required fields
  - 401: Invalid email or password
  - 500: Server error

### Health Check
- **Endpoint**: `GET /api/health`
- **Description**: Check if the API is running
- **Response** (200):
\`\`\`json
{
  "status": "ok"
}
\`\`\`

## Validation Rules

- **Email**: Must be a valid email format (e.g., user@example.com)
- **Password**: Minimum 6 characters
- **Duplicate Email**: Cannot register with an email that already exists

## Database Schema

### Users Table
\`\`\`sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
\`\`\`

## Error Codes

- `400`: Bad Request (missing or invalid fields)
- `401`: Unauthorized (invalid credentials)
- `409`: Conflict (email already registered)
- `500`: Internal Server Error

## Testing with Swagger UI

1. Start the application: `python main.py`
2. Open `http://localhost:8000/api/docs` in your browser
3. Click on the endpoint you want to test
4. Click "Try it out"
5. Enter the request parameters
6. Click "Execute"
7. View the response

## Adding New Features

The modular architecture makes it easy to add new features:

1. **Add a new schema** in `schemas.py` for request/response validation
2. **Add business logic** in `services/` (create a new service file if needed)
3. **Add endpoints** in `routes/` (create a new route file if needed)
4. **Include the router** in `main.py` with `app.include_router()`

Example: To add user profile management, create `services/profile_service.py` and `routes/profile.py`, then include it in `main.py`.

## Future Phases

Phase 1 will add:
- Event Management (create, view, delete events)
- Event Organizer and Attendee roles
- Event invitations

Phase 2 will add:
- Response Management (attendance status)
- Advanced search and filtering
