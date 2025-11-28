import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)

def test_signup_success():
    payload = {
        "email": "testuser@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print_response("Signup - Success", response)

def test_signup_duplicate_email():
    payload = {
        "email": "testuser@example.com",
        "password": "password456"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print_response("Signup - Duplicate Email", response)

def test_signup_invalid_email():
    payload = {
        "email": "invalid-email",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print_response("Signup - Invalid Email", response)

def test_signup_weak_password():
    payload = {
        "email": "newuser@example.com",
        "password": "123"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print_response("Signup - Weak Password", response)

def test_signup_missing_fields():
    payload = {
        "email": "newuser@example.com"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    print_response("Signup - Missing Password", response)

def test_login_success():
    payload = {
        "email": "testuser@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_response("Login - Success", response)

def test_login_invalid_password():
    payload = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_response("Login - Invalid Password", response)

def test_login_nonexistent_user():
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_response("Login - Non-existent User", response)

def test_login_missing_fields():
    payload = {
        "email": "testuser@example.com"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_response("Login - Missing Password", response)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("EventPlanner Phase 0 - API Test Suite")
    print("="*60)
    print("Make sure the Flask app is running: python app.py")
    
    try:
        test_health_check()
        
        test_signup_success()
        test_signup_duplicate_email()
        test_signup_invalid_email()
        test_signup_weak_password()
        test_signup_missing_fields()
        
        test_login_success()
        test_login_invalid_password()
        test_login_nonexistent_user()
        test_login_missing_fields()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the Flask app.")
        print("Make sure to run: python app.py")
