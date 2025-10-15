"""
Simple test to verify JWT authentication is working
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_jwt_auth():
    print("=" * 60)
    print("JWT Authentication Test")
    print("=" * 60)

    # Login
    username = input("Enter username or login_master_id: ")
    password = input("Enter password: ")

    # Try as login_master_id first
    login_payload = {
        "password": password
    }

    # Check if input is numeric (likely login_master_id)
    if username.isdigit():
        login_payload["login_master_id"] = username
    else:
        login_payload["username"] = username

    print(f"\nLogin payload: {login_payload}")

    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_payload)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return

    login_data = login_response.json()
    if not login_data.get('success'):
        print(f"Login failed: {login_data.get('message')}")
        return

    access_token = login_data['data']['access']
    user_info = login_data['data']['user']

    print("\n✅ Login successful!")
    print(f"User info:")
    print(f"  login_master_id: {user_info.get('login_master_id')}")
    print(f"  username: {user_info.get('username')}")
    print(f"  id: {user_info.get('id')}")

    # Test authenticated endpoints
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("\n" + "-" * 40)
    print("Testing authenticated endpoints:")

    # Test profile
    print("\n1. GET /api/v1/auth/profile/")
    profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print(f"   Status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        if profile_data.get('success'):
            print("   ✅ Profile retrieved successfully")
            user_profile = profile_data.get('data', {})
            print(f"   Username: {user_profile.get('username')}")
            print(f"   Login Master ID: {user_profile.get('login_master_id')}")
    else:
        print(f"   ❌ Error: {profile_response.json()}")

    # Test profile update
    print("\n2. PUT /api/v1/auth/profile/")
    update_payload = {
        "email": "test_update@example.com"
    }
    update_response = requests.put(f"{BASE_URL}/auth/profile/", headers=headers, json=update_payload)
    print(f"   Status: {update_response.status_code}")
    if update_response.status_code == 200:
        print("   ✅ Profile update endpoint working")
    else:
        print(f"   ❌ Error: {update_response.json()}")

    # Test password change (just validation)
    print("\n3. POST /api/v1/auth/change-password/")
    pwd_payload = {
        "old_password": "wrong_password",
        "new_password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    pwd_response = requests.post(f"{BASE_URL}/auth/change-password/", headers=headers, json=pwd_payload)
    print(f"   Status: {pwd_response.status_code}")
    if pwd_response.status_code == 400:
        print("   ✅ Password change validation working (correctly rejected wrong password)")
    else:
        print(f"   Response: {pwd_response.json()}")

    print("\n" + "=" * 60)
    print("Summary:")
    if profile_response.status_code == 200:
        print("✅ JWT authentication is working correctly!")
        print("✅ User is properly identified from token")
    else:
        print("❌ JWT authentication has issues")
        print("Check the server logs for details")

if __name__ == "__main__":
    test_jwt_auth()