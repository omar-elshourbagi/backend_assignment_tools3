import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_signup():
    print("\n=== Testing User Registration ===")
    
    print("\n1. Valid signup:")
    response = requests.post(f'{BASE_URL}/auth/signup', json={
        'email': 'user1@example.com',
        'password': 'password123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Duplicate email:")
    response = requests.post(f'{BASE_URL}/auth/signup', json={
        'email': 'user1@example.com',
        'password': 'password456'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n3. Invalid email format:")
    response = requests.post(f'{BASE_URL}/auth/signup', json={
        'email': 'invalid-email',
        'password': 'password123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n4. Weak password (less than 6 characters):")
    response = requests.post(f'{BASE_URL}/auth/signup', json={
        'email': 'user2@example.com',
        'password': '123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n5. Missing email:")
    response = requests.post(f'{BASE_URL}/auth/signup', json={
        'password': 'password123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_login():
    print("\n\n=== Testing User Login ===")
    
    requests.post(f'{BASE_URL}/auth/signup', json={
        'email': 'testuser@example.com',
        'password': 'testpass123'
    })
    
    print("\n1. Valid login:")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'testpass123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n2. Wrong password:")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'testuser@example.com',
        'password': 'wrongpassword'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n3. Non-existent user:")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n4. Missing password:")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'testuser@example.com'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    print("\n\n=== Testing Health Check ===")
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == '__main__':
    print("EventPlanner Phase 0 - API Tests")
    print("Make sure the Flask app is running on http://localhost:5000")
    
    try:
        test_health()
        test_signup()
        test_login()
        print("\n\n=== All tests completed ===")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask app is running.")
