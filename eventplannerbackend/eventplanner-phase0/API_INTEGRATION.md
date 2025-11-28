# API Integration Guide

This document provides the necessary details to integrate with the EventPlanner API for user authentication.

## Base URL

All endpoints are available under the following base URL:

```
http://localhost:8000
```

---

## Authentication Endpoints

### 1. User Signup

This endpoint allows a new user to register in the system.

- **URL**: `/signup`
- **Method**: `POST`
- **Description**: Creates a new user account.

#### Request Body

The request body must be a JSON object with the following fields:

| Field              | Type   | Description                            | Required |
|--------------------|--------|----------------------------------------|----------|
| `name`             | string | The user's full name.                  | Yes      |
| `email`            | string | The user's email address.              | Yes      |
| `password`         | string | The user's password (min. 6 characters). | Yes      |
| `confirm_password` | string | The user's password for confirmation.  | Yes      |

**Example Request:**

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

#### Responses

- **201 Created**: The user was successfully created.

  **Example Response:**

  ```json
  {
    "user_id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "message": "User registered successfully"
  }
  ```

- **409 Conflict**: The provided email is already registered.

  ```json
  {
    "detail": "Email already registered"
  }
  ```

- **422 Unprocessable Entity**: The request body is invalid (e.g., invalid email format, passwords do not match).

  ```json
  {
    "detail": [
      {
        "loc": ["body", "password"],
        "msg": "ensure this value has at least 6 characters",
        "type": "value_error.any_str.min_length",
        "ctx": { "limit_value": 6 }
      }
    ]
  }
  ```

#### `curl` Example

```bash
curl -X POST "http://localhost:8000/signup" \
-H "Content-Type: application/json" \
-d '{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123"
}'
```

---

### 2. User Login

This endpoint allows an existing user to authenticate.

- **URL**: `/login`
- **Method**: `POST`
- **Description**: Authenticates a user and returns their information.

#### Request Body

The request body must be a JSON object with the following fields:

| Field      | Type   | Description               | Required |
|------------|--------|---------------------------|----------|
| `email`    | string | The user's email address. | Yes      |
| `password` | string | The user's password.      | Yes      |

**Example Request:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Responses

- **200 OK**: The user was successfully authenticated.

  **Example Response:**

  ```json
  {
    "user_id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "message": "Login successful"
  }
  ```

- **401 Unauthorized**: The provided credentials are invalid.

  ```json
  {
    "detail": "Invalid email or password"
  }
  ```

#### `curl` Example

```bash
curl -X POST "http://localhost:8000/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "password123"
}'
```
