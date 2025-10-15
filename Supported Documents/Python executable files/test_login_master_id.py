"""
Test script for login_master_id authentication
This tests the updated JWT authentication that uses login_master_id
"""
import requests
import json

# Base URL - update if running on different port
BASE_URL = "http://localhost:8000/api/v1"

def test_login_with_login_master_id():
    """Test login endpoint with login_master_id"""
    print("=" * 60)
    print("Testing Authentication with login_master_id")
    print("=" * 60)

    # Get credentials from user
    print("\nEnter your login credentials:")
    print("You can now use either login_master_id OR username")
    print("-" * 40)

    login_master_id = input("Login Master ID (press Enter to skip): ").strip()
    username = input("Username (press Enter to skip if using login_master_id): ").strip()
    password = input("Password: ")

    # Prepare payload based on what was provided
    payload = {"password": password}

    if login_master_id:
        payload["login_master_id"] = login_master_id
        print(f"\nUsing login_master_id: {login_master_id}")
    elif username:
        payload["username"] = username
        print(f"\nUsing username: {username}")
    else:
        print("\n❌ Error: You must provide either login_master_id or username")
        return None

    # Login endpoint
    url = f"{BASE_URL}/auth/login/"

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

                print(f"\n📋 User Info:")
                print(f"  ID: {user_info.get('id')}")
                print(f"  Login Master ID: {user_info.get('login_master_id')}")
                print(f"  Username: {user_info.get('username')}")
                print(f"  Email: {user_info.get('email')}")
                print(f"  Role ID: {user_info.get('role_id')}")
                print(f"  Client ID: {user_info.get('client_id')}")
                print(f"  Merchant: {user_info.get('merchant_name')}")

                print(f"\n🔐 JWT Token Claims:")
                # Decode JWT to show claims (without verification for testing)
                import base64
                try:
                    # Split token and decode payload
                    token_parts = access_token.split('.')
                    if len(token_parts) >= 2:
                        # Add padding if needed
                        payload_encoded = token_parts[1]
                        payload_encoded += '=' * (4 - len(payload_encoded) % 4)
                        payload_decoded = base64.b64decode(payload_encoded)
                        claims = json.loads(payload_decoded)

                        print(f"  Token Type: {claims.get('token_type', 'N/A')}")
                        print(f"  Login Master ID in Token: {claims.get('login_master_id', 'N/A')}")
                        print(f"  Username in Token: {claims.get('username', 'N/A')}")
                        print(f"  Role ID in Token: {claims.get('role_id', 'N/A')}")
                        print(f"  Client ID in Token: {claims.get('client_id', 'N/A')}")
                        print(f"  User ID: {claims.get('user_id', 'N/A')}")
                except Exception as e:
                    print(f"  Could not decode token: {e}")

                print(f"\n🔑 Tokens Generated:")
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
        print("\nTo start the server, run:")
        print("  cd sabpaisa-reports-api")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    return None


def test_profile_with_token(token):
    """Test profile endpoint with token that contains login_master_id"""
    print("\n" + "=" * 60)
    print("Testing Profile API with login_master_id Token")
    print("=" * 60)

    url = f"{BASE_URL}/auth/profile/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")

            if data.get('success'):
                profile = data.get('data', {})
                print("\n✅ Profile fetched successfully!")
                print("\n📋 Profile Data:")
                print(f"  Login Master ID: {profile.get('login_master_id', 'N/A')}")
                print(f"  Username: {profile.get('username', 'N/A')}")
                print(f"  Email: {profile.get('email', 'N/A')}")
                print(f"  Name: {profile.get('name', 'N/A')}")
                print(f"  Mobile: {profile.get('mobile', 'N/A')}")
                print(f"  Role ID: {profile.get('role_id', 'N/A')}")
        else:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n❌ Profile fetch failed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_both_authentication_methods():
    """Test that both login_master_id and username authentication work"""
    print("\n" + "=" * 60)
    print("🔄 Testing Both Authentication Methods")
    print("=" * 60)

    print("\n1️⃣  First, test with login_master_id:")
    print("-" * 40)
    token1 = test_login_with_login_master_id()

    print("\n\n2️⃣  Now, test with username:")
    print("-" * 40)
    token2 = test_login_with_login_master_id()

    if token1 and token2:
        print("\n" + "=" * 60)
        print("✅ Both authentication methods are working!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  One or both authentication methods failed")
        print("=" * 60)


if __name__ == "__main__":
    print("SabPaisa Reports API - Login Master ID Authentication Test")
    print("=" * 60)
    print("\n📌 Features Added:")
    print("  • JWT token generation now uses login_master_id as primary identifier")
    print("  • Can authenticate with either login_master_id OR username")
    print("  • Token includes login_master_id in claims")
    print("  • Profile endpoint works with login_master_id-based tokens")
    print("\n" + "=" * 60)

    # Main test
    print("\n🧪 Starting Authentication Test...")
    token = test_login_with_login_master_id()

    # If login successful, test profile
    if token:
        test_profile_with_token(token)

    # Optional: Test both methods
    print("\n" + "=" * 60)
    choice = input("\nDo you want to test both authentication methods? (y/n): ")
    if choice.lower() == 'y':
        test_both_authentication_methods()

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)