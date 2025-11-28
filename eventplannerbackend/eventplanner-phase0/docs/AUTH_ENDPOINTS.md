# Authentication Endpoints

## Get Current User (Who is Logged In)

Get the currently logged-in user's information.

### Endpoint
```
GET /me?user_id={user_id}
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | The logged-in user's ID (stored after login) |

### Success Response (200 OK)
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Error Responses

#### 404 Not Found - User doesn't exist
```json
{
  "detail": "User not found"
}
```

### Frontend Example (JavaScript/Axios)
```javascript
const getCurrentUser = async () => {
  const userId = localStorage.getItem('user_id');
  
  if (!userId) {
    console.log('No user logged in');
    return null;
  }
  
  try {
    const response = await axios.get(`http://localhost:8000/me?user_id=${userId}`);
    console.log('Current user:', response.data);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      // User not found - clear stored data
      localStorage.removeItem('user_id');
      console.log('User session invalid');
    }
    throw error;
  }
};

// Usage in React
const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Please login</div>;

  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      <p>Email: {user.email}</p>
    </div>
  );
};
```

---

## Get All Users

Get all registered users in the application.

### Endpoint
```
GET /users
```

### No Parameters Required

### Success Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com"
  }
]
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | User's unique ID |
| name | string | User's full name |
| email | string | User's email address |

### Frontend Example (JavaScript/Axios)
```javascript
const getAllUsers = async () => {
  try {
    const response = await axios.get('http://localhost:8000/users');
    console.log('Users:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch users:', error);
    throw error;
  }
};

// Usage - Get users to invite to an event
const UserSelector = ({ onSelectUser }) => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    getAllUsers().then(setUsers);
  }, []);

  return (
    <select onChange={(e) => onSelectUser(e.target.value)}>
      <option value="">Select a user...</option>
      {users.map(user => (
        <option key={user.id} value={user.id}>
          {user.name} ({user.email})
        </option>
      ))}
    </select>
  );
};
```

---

## Signup

Register a new user account.

### Endpoint
```
POST /signup
```

### Request Body
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | User's full name |
| email | string | Yes | Valid email address |
| password | string | Yes | Password (minimum 6 characters) |
| confirm_password | string | Yes | Must match password |

### Success Response (201 Created)
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "message": "User registered successfully"
}
```

### Error Responses

#### 400 Bad Request - Passwords don't match
```json
{
  "detail": "Passwords do not match"
}
```

#### 409 Conflict - Email already exists
```json
{
  "detail": "Email already registered"
}
```

### Frontend Example (JavaScript/Axios)
```javascript
const signup = async (userData) => {
  try {
    const response = await axios.post('http://localhost:8000/signup', {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      confirm_password: userData.confirmPassword
    });
    
    console.log('User created:', response.data);
    return response.data;
  } catch (error) {
    if (error.response?.status === 409) {
      alert('Email already registered');
    } else {
      alert(error.response?.data?.detail || 'Signup failed');
    }
    throw error;
  }
};
```

---

## Login

Authenticate user and receive JWT token.

### Endpoint
```
POST /login
```

### Request Body
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |

### Success Response (200 OK)
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| user_id | integer | User's unique ID (use for all subsequent requests) |
| name | string | User's full name |
| email | string | User's email |
| token | string | JWT token (not currently required but generated) |
| message | string | Success message |

### Error Responses

#### 401 Unauthorized - Invalid credentials
```json
{
  "detail": "Invalid email or password"
}
```

### Frontend Example (JavaScript/Axios)
```javascript
const login = async (email, password) => {
  try {
    const response = await axios.post('http://localhost:8000/login', {
      email,
      password
    });
    
    // Store user_id in localStorage or state management
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('user_name', response.data.name);
    localStorage.setItem('token', response.data.token);
    
    console.log('Login successful:', response.data);
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      alert('Invalid email or password');
    } else {
      alert('Login failed');
    }
    throw error;
  }
};
```

### Frontend Example (React with Axios)
```jsx
import { useState } from 'react';
import axios from 'axios';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('http://localhost:8000/login', {
        email,
        password
      });
      
      // Store user data
      localStorage.setItem('user_id', response.data.user_id);
      
      // Redirect or update UI
      window.location.href = '/dashboard';
    } catch (error) {
      alert(error.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required 
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required 
      />
      <button type="submit">Login</button>
    </form>
  );
};
```

