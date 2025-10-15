"""
Debug script to test JWT token decoding and authentication
"""
import os
import sys
from pathlib import Path
import django

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json
import base64
from rest_framework_simplejwt.tokens import AccessToken
from apps.authentication.backends import CustomJWTAuthentication, SimpleUser

BASE_URL = "http://localhost:8000/api/v1"

def decode_jwt_payload(token):
    """Decode JWT token payload without verification"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_jwt_authentication():
    """Test JWT authentication backend"""
    print("=" * 60)
    print("JWT Authentication Debug Test")
    print("=" * 60)

    # Step 1: Login to get token
    print("\n1. Login to get JWT token")
    print("-" * 40)

    username = input("Username (or press Enter to skip): ").strip()
    login_master_id = input("Login Master ID (or press Enter to skip): ").strip()
    password = input("Password: ")

    payload = {"password": password}
    if login_master_id:
        payload["login_master_id"] = login_master_id
    elif username:
        payload["username"] = username
    else:
        print("❌ Must provide either username or login_master_id")
        return

    # Login
    login_url = f"{BASE_URL}/auth/login/"
    try:
        response = requests.post(login_url, json=payload)

        if response.status_code != 200:
            print(f"❌ Login failed with status {response.status_code}")
            print(response.text)
            return

        data = response.json()
        if not data.get('success'):
            print(f"❌ Login failed: {data.get('message')}")
            return

        access_token = data['data']['access']
        user_info = data['data']['user']

        print("✅ Login successful!")
        print(f"\nUser info from login response:")
        print(f"  login_master_id: {user_info.get('login_master_id')}")
        print(f"  username: {user_info.get('username')}")
        print(f"  id: {user_info.get('id')}")

        # Step 2: Decode JWT token
        print("\n2. Decode JWT Token")
        print("-" * 40)

        payload = decode_jwt_payload(access_token)
        if payload:
            print("JWT Payload contents:")
            for key, value in payload.items():
                if key != 'exp' and key != 'iat' and key != 'jti':
                    print(f"  {key}: {value}")

        # Step 3: Test Django JWT decoder
        print("\n3. Test Django JWT Decoder")
        print("-" * 40)

        try:
            # Use Django's JWT decoder
            token_obj = AccessToken(access_token)
            print("Django AccessToken decoded:")
            print(f"  login_master_id: {token_obj.get('login_master_id')}")
            print(f"  username: {token_obj.get('username')}")
            print(f"  user_id: {token_obj.get('user_id')}")
            print(f"  role_id: {token_obj.get('role_id')}")
        except Exception as e:
            print(f"❌ Error decoding with Django: {e}")

        # Step 4: Test Custom JWT Authentication backend
        print("\n4. Test Custom JWT Authentication Backend")
        print("-" * 40)

        try:
            auth = CustomJWTAuthentication()

            # Create a mock request
            class MockRequest:
                def __init__(self, token):
                    self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

            mock_request = MockRequest(access_token)

            # Test authentication
            result = auth.authenticate(mock_request)

            if result:
                user, validated_token = result
                print(f"✅ Authentication successful!")
                print(f"User object created:")
                print(f"  Type: {type(user).__name__}")
                print(f"  username: {getattr(user, 'username', 'N/A')}")
                print(f"  login_master_id: {getattr(user, 'login_master_id', 'N/A')}")
                print(f"  pk: {getattr(user, 'pk', 'N/A')}")
                print(f"  id: {getattr(user, 'id', 'N/A')}")
                print(f"  role_id: {getattr(user, 'role_id', 'N/A')}")
            else:
                print("❌ Authentication returned None")
        except Exception as e:
            print(f"❌ Authentication error: {e}")

        # Step 5: Test API endpoints with token
        print("\n5. Test API Endpoints")
        print("-" * 40)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Test profile endpoint
        print("\nTesting GET /api/v1/auth/profile/")
        profile_response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Status: {profile_response.status_code}")
        if profile_response.status_code == 200:
            print("✅ Profile retrieved successfully")
        else:
            print(f"❌ Profile failed: {profile_response.json().get('message')}")

        # Test change password endpoint (without actually changing)
        print("\nTesting POST /api/v1/auth/change-password/ (validation only)")
        change_pwd_payload = {
            "old_password": "wrong_password",
            "new_password": "TestPass123",
            "confirm_password": "TestPass123"
        }
        change_response = requests.post(
            f"{BASE_URL}/auth/change-password/",
            headers=headers,
            json=change_pwd_payload
        )
        print(f"Status: {change_response.status_code}")
        if change_response.status_code == 400:
            print("✅ Correctly rejected wrong password")
        else:
            print(f"Response: {change_response.json()}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Debug Summary")
    print("=" * 60)
    print("\nIf 'unknown' appears in logs, check:")
    print("1. JWT token contains correct user identifiers")
    print("2. CustomJWTAuthentication is extracting them properly")
    print("3. Views are reading from request.user correctly")

if __name__ == "__main__":
    test_jwt_authentication()