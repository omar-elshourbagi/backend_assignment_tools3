# Frontend Integration Guide

## Quick Start

### Prerequisites
- API running on `http://localhost:8000`
- Axios or Fetch API for HTTP requests

### Installation

```bash
npm install axios
# or
yarn add axios
```

---

## Setup Axios Instance

Create a reusable Axios instance with base configuration:

```javascript
// src/api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## API Service Layer

Create service files to organize API calls:

### Auth Service

```javascript
// src/api/authService.js
import apiClient from './client';

export const authService = {
  async signup(name, email, password, confirmPassword) {
    const response = await apiClient.post('/signup', {
      name,
      email,
      password,
      confirm_password: confirmPassword
    });
    return response.data;
  },

  async login(email, password) {
    const response = await apiClient.post('/login', {
      email,
      password
    });
    
    // Store user data
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('user_name', response.data.name);
    localStorage.setItem('token', response.data.token);
    
    return response.data;
  },

  logout() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('token');
  },

  getCurrentUserId() {
    return localStorage.getItem('user_id');
  },

  isAuthenticated() {
    return !!this.getCurrentUserId();
  }
};
```

### Event Service

```javascript
// src/api/eventService.js
import apiClient from './client';

export const eventService = {
  async createEvent(userId, eventData) {
    const response = await apiClient.post(`/events?user_id=${userId}`, eventData);
    return response.data;
  },

  async getOrganizedEvents(userId) {
    const response = await apiClient.get(`/events/organized?user_id=${userId}`);
    return response.data;
  },

  async getInvitedEvents(userId) {
    const response = await apiClient.get(`/events/invited?user_id=${userId}`);
    return response.data;
  },

  async getEventAttendees(eventId, userId) {
    const response = await apiClient.get(
      `/events/${eventId}/attendees?user_id=${userId}`
    );
    return response.data;
  },

  async inviteUser(eventId, inviterId, userIdToInvite) {
    const response = await apiClient.post(
      `/events/${eventId}/invite?inviter_id=${inviterId}`,
      { userId: userIdToInvite }
    );
    return response.data;
  },

  async updateAttendanceStatus(eventId, userId, status) {
    const response = await apiClient.put(
      `/events/${eventId}/attendance?user_id=${userId}`,
      { status }
    );
    return response.data;
  },

  async deleteEvent(eventId, userId) {
    await apiClient.delete(`/events/${eventId}?user_id=${userId}`);
  },

  async searchEvents(userId, filters) {
    const params = new URLSearchParams({ user_id: userId });
    
    if (filters.keyword) params.append('keyword', filters.keyword);
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);
    if (filters.role) params.append('role', filters.role);
    if (filters.location) params.append('location', filters.location);
    if (filters.status) params.append('attendance_status', filters.status);
    
    const response = await apiClient.get(`/events/search?${params.toString()}`);
    return response.data;
  }
};
```

---

## Common Integration Patterns

### 1. User Authentication Flow

```javascript
// Login Component
import { useState } from 'react';
import { authService } from '../api/authService';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await authService.login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
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

### 2. Create Event Form

```javascript
import { useState } from 'react';
import { eventService } from '../api/eventService';
import { authService } from '../api/authService';

const CreateEventForm = ({ onEventCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    time: '',
    location: '',
    description: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const userId = authService.getCurrentUserId();
    
    try {
      const newEvent = await eventService.createEvent(userId, formData);
      alert('Event created successfully!');
      onEventCreated(newEvent);
    } catch (error) {
      alert('Failed to create event');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Event Title"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        required
      />
      <input
        type="date"
        value={formData.date}
        onChange={(e) => setFormData({...formData, date: e.target.value})}
        required
      />
      <input
        type="time"
        value={formData.time}
        onChange={(e) => setFormData({...formData, time: e.target.value + ':00'})}
        required
      />
      <input
        type="text"
        placeholder="Location"
        value={formData.location}
        onChange={(e) => setFormData({...formData, location: e.target.value})}
        required
      />
      <textarea
        placeholder="Description (optional)"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
      />
      <button type="submit">Create Event</button>
    </form>
  );
};
```

### 3. Event List Component

```javascript
import { useState, useEffect } from 'react';
import { eventService } from '../api/eventService';
import { authService } from '../api/authService';

const MyEvents = () => {
  const [organizedEvents, setOrganizedEvents] = useState([]);
  const [invitedEvents, setInvitedEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    const userId = authService.getCurrentUserId();
    
    try {
      const [organized, invited] = await Promise.all([
        eventService.getOrganizedEvents(userId),
        eventService.getInvitedEvents(userId)
      ]);
      
      setOrganizedEvents(organized);
      setInvitedEvents(invited);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <section>
        <h2>Events I'm Organizing</h2>
        {organizedEvents.map(event => (
          <EventCard key={event.id} event={event} isOrganizer />
        ))}
      </section>

      <section>
        <h2>Events I'm Invited To</h2>
        {invitedEvents.map(event => (
          <EventCard key={event.id} event={event} isOrganizer={false} />
        ))}
      </section>
    </div>
  );
};
```

### 4. Event Card with Attendance Buttons

```javascript
import { useState } from 'react';
import { eventService } from '../api/eventService';
import { authService } from '../api/authService';

const EventCard = ({ event, isOrganizer }) => {
  const userId = parseInt(authService.getCurrentUserId());
  const userAttendee = event.attendees.find(a => a.user_id === userId);
  const [status, setStatus] = useState(userAttendee?.attendance_status || 'pending');

  const handleStatusChange = async (newStatus) => {
    try {
      await eventService.updateAttendanceStatus(event.id, userId, newStatus);
      setStatus(newStatus);
    } catch (error) {
      alert('Failed to update status');
    }
  };

  const handleDelete = async () => {
    if (confirm('Delete this event?')) {
      try {
        await eventService.deleteEvent(event.id, userId);
        window.location.reload();
      } catch (error) {
        alert('Failed to delete event');
      }
    }
  };

  return (
    <div className="event-card">
      <h3>{event.title}</h3>
      <p>📅 {event.date} at {event.time}</p>
      <p>📍 {event.location}</p>
      {event.description && <p>{event.description}</p>}
      
      <div className="attendees">
        <p>Attendees: {event.attendees.length}</p>
        <div>
          {event.attendees.filter(a => a.attendance_status === 'going').length} Going
        </div>
      </div>

      {!isOrganizer && (
        <div className="attendance-buttons">
          <button
            onClick={() => handleStatusChange('going')}
            className={status === 'going' ? 'active' : ''}
          >
            ✓ Going
          </button>
          <button
            onClick={() => handleStatusChange('maybe')}
            className={status === 'maybe' ? 'active' : ''}
          >
            ? Maybe
          </button>
          <button
            onClick={() => handleStatusChange('not_going')}
            className={status === 'not_going' ? 'active' : ''}
          >
            ✗ Can't Go
          </button>
        </div>
      )}

      {isOrganizer && (
        <button onClick={handleDelete} className="delete-btn">
          Delete Event
        </button>
      )}
    </div>
  );
};
```

### 5. Search Component

```javascript
import { useState } from 'react';
import { eventService } from '../api/eventService';
import { authService } from '../api/authService';

const EventSearch = () => {
  const [filters, setFilters] = useState({
    keyword: '',
    startDate: '',
    endDate: '',
    role: '',
    location: ''
  });
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const userId = authService.getCurrentUserId();
    
    try {
      const events = await eventService.searchEvents(userId, {
        keyword: filters.keyword,
        startDate: filters.startDate,
        endDate: filters.endDate,
        role: filters.role,
        location: filters.location
      });
      
      setResults(events);
    } catch (error) {
      alert('Search failed');
    }
  };

  return (
    <div>
      <div className="search-form">
        <input
          type="text"
          placeholder="Search events..."
          value={filters.keyword}
          onChange={(e) => setFilters({...filters, keyword: e.target.value})}
        />
        <input
          type="date"
          placeholder="Start Date"
          value={filters.startDate}
          onChange={(e) => setFilters({...filters, startDate: e.target.value})}
        />
        <input
          type="date"
          placeholder="End Date"
          value={filters.endDate}
          onChange={(e) => setFilters({...filters, endDate: e.target.value})}
        />
        <select
          value={filters.role}
          onChange={(e) => setFilters({...filters, role: e.target.value})}
        >
          <option value="">All Events</option>
          <option value="organizer">My Organized Events</option>
          <option value="attendee">Events I'm Attending</option>
        </select>
        <button onClick={handleSearch}>Search</button>
      </div>

      <div className="results">
        {results.map(event => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  );
};
```

---

## Environment Configuration

Create an environment file for different deployment environments:

```javascript
// src/config/env.js
const ENV = {
  development: {
    API_URL: 'http://localhost:8000'
  },
  production: {
    API_URL: 'https://api.yourapp.com'
  }
};

export const config = ENV[process.env.NODE_ENV || 'development'];
```

Use in API client:
```javascript
import { config } from '../config/env';

const apiClient = axios.create({
  baseURL: config.API_URL
});
```

---

## Error Handling Best Practices

```javascript
// src/utils/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    switch (error.response.status) {
      case 400:
        return error.response.data.detail || 'Invalid request';
      case 401:
        return 'Please login to continue';
      case 403:
        return 'You don't have permission for this action';
      case 404:
        return 'Resource not found';
      case 409:
        return 'This resource already exists';
      case 500:
        return 'Server error. Please try again later';
      default:
        return 'Something went wrong';
    }
  } else if (error.request) {
    // Request made but no response
    return 'Cannot connect to server';
  } else {
    return error.message;
  }
};

// Usage
try {
  await eventService.createEvent(userId, eventData);
} catch (error) {
  const message = handleApiError(error);
  alert(message);
}
```

---

## Testing API Calls

```javascript
// Example with Jest
import { eventService } from './eventService';
import axios from 'axios';

jest.mock('axios');

describe('eventService', () => {
  test('createEvent makes correct API call', async () => {
    const mockEvent = { id: 1, title: 'Test Event' };
    axios.post.mockResolvedValue({ data: mockEvent });

    const result = await eventService.createEvent(1, {
      title: 'Test Event',
      date: '2025-12-15',
      time: '14:00:00',
      location: 'Test Location'
    });

    expect(result).toEqual(mockEvent);
    expect(axios.post).toHaveBeenCalledWith(
      '/events?user_id=1',
      expect.any(Object)
    );
  });
});
```

