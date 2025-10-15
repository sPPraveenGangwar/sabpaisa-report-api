"""
Debug script for testing profile endpoint
"""
import requests
import json
import base64

BASE_URL = "http://localhost:8000/api/v1"

def decode_jwt_token(token):
    """Decode JWT token to see its contents"""
    try:
        # Split token
        parts = token.split('.')
        if len(parts) != 3:
            print("Invalid token format")
            return None

        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_login_and_profile():
    """Test login and then profile endpoint"""
    print("=" * 60)
    print("Testing Login and Profile Endpoints")
    print("=" * 60)

    # Get credentials
    print("\nEnter login credentials:")
    username = input("Username (or press Enter to skip): ").strip()
    login_master_id = input("Login Master ID (or press Enter to skip): ").strip()
    password = input("Password: ")

    # Prepare login payload
    payload = {"password": password}
    if login_master_id:
        payload["login_master_id"] = login_master_id
    elif username:
        payload["username"] = username
    else:
        print("❌ Must provide either username or login_master_id")
        return

    # 1. Login
    print("\n" + "=" * 40)
    print("1. Testing Login")
    print("-" * 40)

    login_url = f"{BASE_URL}/auth/login/"
    print(f"POST {login_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(login_url, json=payload)
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Login successful!")

                access_token = data['data']['access']
                user_info = data['data']['user']

                print("\nUser Info from Login:")
                print(f"  ID: {user_info.get('id')}")
                print(f"  Login Master ID: {user_info.get('login_master_id')}")
                print(f"  Username: {user_info.get('username')}")

                # Decode token
                print("\nJWT Token Contents:")
                token_data = decode_jwt_token(access_token)
                if token_data:
                    print(f"  login_master_id: {token_data.get('login_master_id')}")
                    print(f"  username: {token_data.get('username')}")
                    print(f"  user_id: {token_data.get('user_id')}")
                    print(f"  exp: {token_data.get('exp')}")

                # 2. Test Profile GET
                print("\n" + "=" * 40)
                print("2. Testing Profile GET")
                print("-" * 40)

                profile_url = f"{BASE_URL}/auth/profile/"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                print(f"GET {profile_url}")
                print(f"Headers: Authorization: Bearer {access_token[:50]}...")

                profile_response = requests.get(profile_url, headers=headers)
                print(f"\nStatus: {profile_response.status_code}")
                print(f"Response: {json.dumps(profile_response.json(), indent=2)}")

                if profile_response.status_code == 200:
                    print("✅ Profile retrieved successfully!")
                elif profile_response.status_code == 404:
                    print("❌ User not found in database")
                    print("\nPossible issues:")
                    print("1. Token doesn't contain correct user identifier")
                    print("2. Database query is using wrong column")
                    print("3. User doesn't exist in database")
                elif profile_response.status_code == 401:
                    print("❌ Authentication failed")
                    print("Token might be invalid or expired")
                else:
                    print(f"❌ Unexpected status code: {profile_response.status_code}")

                # 3. Test Profile PUT (should return stub message)
                print("\n" + "=" * 40)
                print("3. Testing Profile PUT")
                print("-" * 40)

                print(f"PUT {profile_url}")
                put_response = requests.put(
                    profile_url,
                    headers=headers,
                    json={"name": "Test Update"}
                )
                print(f"Status: {put_response.status_code}")
                print(f"Response: {json.dumps(put_response.json(), indent=2)}")

            else:
                print(f"❌ Login failed: {data.get('message')}")
        else:
            print(f"❌ Login request failed with status {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Profile Endpoint Debug Tool")
    print("=" * 60)
    print("This tool will:")
    print("1. Login with your credentials")
    print("2. Decode the JWT token to show its contents")
    print("3. Test the profile GET endpoint")
    print("4. Test the profile PUT endpoint")
    print("=" * 60)

    test_login_and_profile()

    print("\n" + "=" * 60)
    print("Debug complete! Check the server logs for detailed information.")
    print("=" * 60)