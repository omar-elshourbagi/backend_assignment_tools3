# Health Check Endpoint

## Health Check

Check if the API server is running and healthy.

### Endpoint
```
GET /health
```

### No Parameters Required

### Success Response (200 OK)
```json
{
  "status": "ok"
}
```

### Frontend Example
```javascript
const checkHealth = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health');
    console.log('API Status:', response.data.status);
    return response.data.status === 'ok';
  } catch (error) {
    console.error('API is down');
    return false;
  }
};

// Usage - Check health on app startup
useEffect(() => {
  checkHealth().then(isHealthy => {
    if (!isHealthy) {
      alert('Cannot connect to API server');
    }
  });
}, []);
```

