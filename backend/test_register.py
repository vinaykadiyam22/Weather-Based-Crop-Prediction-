import requests
import json

url = "http://localhost:8000/api/auth/register"
data = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "location": "Test Location",
    "password": "testpassword",
    "language": "en"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
