"""
Test script for authentication APIs
Run this to test login functionality
"""
import requests
import json

# Base URL - update if running on different port
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login endpoint"""
    print("=" * 60)
    print("Testing Authentication API")
    print("=" * 60)

    # Get credentials from user
    print("\nEnter your login credentials from the login_master table:")
    username = input("Username: ")
    password = input("Password: ")

    # Login endpoint
    url = f"{BASE_URL}/auth/login/"
    payload = {
        "username": username,
        "password": password
    }

    print(f"\nTesting login at: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✅ Login Successful!")
                access_token = data['data']['access']
                refresh_token = data['data']['refresh']
                user_info = data['data']['user']

                print(f"\nUser Info:")
                print(f"  Username: {user_info.get('username')}")
                print(f"  Role: {user_info.get('role')}")
                print(f"  Merchant: {user_info.get('merchant_name')}")
                print(f"  Is Admin: {user_info.get('is_admin')}")

                print(f"\nTokens Generated:")
                print(f"  Access Token (first 50 chars): {access_token[:50]}...")
                print(f"  Refresh Token (first 50 chars): {refresh_token[:50]}...")

                return access_token
            else:
                print("\n❌ Login Failed!")
                print(f"Message: {data.get('message')}")
        else:
            print("\n❌ Request Failed!")

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure Django server is running on port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    return None


def test_profile(token):
    """Test profile endpoint"""
    print("\n" + "=" * 60)
    print("Testing Profile API")
    print("=" * 60)

    url = f"{BASE_URL}/auth/profile/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Profile fetched successfully!")
        else:
            print("\n❌ Profile fetch failed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_health():
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Check")
    print("=" * 60)

    url = f"{BASE_URL}/auth/health/"

    try:
        response = requests.get(url)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Health check passed!")
        else:
            print("\n❌ Health check failed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("SabPaisa Reports API - Authentication Test")
    print("=" * 60)

    # Test health check first
    test_health()

    # Test login
    token = test_login()

    # If login successful, test profile
    if token:
        test_profile(token)

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)