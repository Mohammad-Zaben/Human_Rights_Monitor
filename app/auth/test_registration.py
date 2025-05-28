import requests

# Test registration endpoint
def test_registration():
    url = "http://localhost:8000/users/register"
    payload = {
        "username": "testuser1",
        "email": "testuser1@example.com",
        "role": "user",
        "password": "testpassword123"
    }
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == "__main__":
    test_registration()
