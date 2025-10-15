"""
Test script for user sessions endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_sessions():
    """Test sessions endpoint"""
    print("=" * 60)
    print("User Sessions Test")
    print("=" * 60)

    # Step 1: Login to get access token
    print("\n1. Login to get access token")
    print("-" * 40)

    username = input("Username or Login Master ID: ")
    password = input("Password: ")

    # Prepare login payload
    payload = {"password": password}

    # Check if it's a number (likely login_master_id)
    if username.isdigit():
        payload["login_master_id"] = username
        print(f"Using login_master_id: {username}")
    else:
        payload["username"] = username
        print(f"Using username: {username}")

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
        refresh_token = data['data']['refresh']
        user_info = data['data']['user']

        print("✅ Login successful!")
        print(f"\nLogged in as:")
        print(f"  Login Master ID: {user_info.get('login_master_id')}")
        print(f"  Username: {user_info.get('username')}")
        print(f"  Role ID: {user_info.get('role_id')}")

        # Step 2: Get sessions
        print("\n2. Get user sessions")
        print("-" * 40)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        sessions_url = f"{BASE_URL}/auth/sessions/"
        print(f"GET {sessions_url}")

        sessions_response = requests.get(sessions_url, headers=headers)
        print(f"Response status: {sessions_response.status_code}")

        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()

            if sessions_data.get('success'):
                print("\n✅ Sessions retrieved successfully!")

                # Display metadata
                metadata = sessions_data.get('metadata', {})
                print(f"\n📊 Session Metadata:")
                print(f"  Total sessions: {metadata.get('total_sessions', 0)}")
                print(f"  Current session ID: {metadata.get('current_session_id', 'N/A')}")

                user_meta = metadata.get('user', {})
                print(f"  User: {user_meta.get('username')} (ID: {user_meta.get('login_master_id')})")

                # Display session data
                sessions = sessions_data.get('data', [])

                if sessions:
                    print(f"\n📋 Active Sessions ({len(sessions)}):")
                    print("-" * 40)

                    for i, session in enumerate(sessions, 1):
                        print(f"\nSession #{i}:")
                        print(f"  Session ID: {session.get('session_id')}")
                        print(f"  User ID: {session.get('user_id')}")
                        print(f"  Login Master ID: {session.get('login_master_id')}")
                        print(f"  Username: {session.get('username')}")
                        print(f"  Token Type: {session.get('token_type')}")
                        print(f"  Created: {session.get('created_at')}")
                        print(f"  Expires: {session.get('expires_at')}")
                        print(f"  Duration: {session.get('duration_readable')}")
                        print(f"  Active: {session.get('is_active')}")
                        print(f"  IP Address: {session.get('ip_address')}")
                        print(f"  User Agent: {session.get('user_agent', 'N/A')[:50]}...")
                        print(f"  Role ID: {session.get('role_id')}")
                        print(f"  Client ID: {session.get('client_id')}")

                        # Calculate time remaining
                        if session.get('expires_at'):
                            try:
                                expires = datetime.fromisoformat(session.get('expires_at').replace('Z', '+00:00'))
                                now = datetime.now(expires.tzinfo)
                                remaining = expires - now

                                if remaining.total_seconds() > 0:
                                    hours = int(remaining.total_seconds() // 3600)
                                    minutes = int((remaining.total_seconds() % 3600) // 60)
                                    print(f"  Time remaining: {hours}h {minutes}m")
                                else:
                                    print(f"  Time remaining: Expired")
                            except:
                                pass
                else:
                    print("\n⚠️  No active sessions found")
            else:
                print(f"\n❌ Failed to get sessions: {sessions_data.get('message')}")
        else:
            print(f"\n❌ Request failed with status {sessions_response.status_code}")
            print(f"Response: {sessions_response.text}")

        # Step 3: Test with multiple logins (optional)
        print("\n" + "=" * 40)
        test_multiple = input("\nTest multiple sessions? (y/n): ")

        if test_multiple.lower() == 'y':
            print("\n3. Creating another session")
            print("-" * 40)

            # Login again to create another token
            response2 = requests.post(login_url, json=payload)
            if response2.status_code == 200:
                data2 = response2.json()
                if data2.get('success'):
                    access_token2 = data2['data']['access']
                    print("✅ Second login successful!")

                    # Get sessions with new token
                    headers2 = {
                        "Authorization": f"Bearer {access_token2}",
                        "Content-Type": "application/json"
                    }

                    sessions_response2 = requests.get(sessions_url, headers=headers2)
                    if sessions_response2.status_code == 200:
                        sessions_data2 = sessions_response2.json()
                        print(f"Sessions with new token: {sessions_data2.get('metadata', {}).get('total_sessions', 0)}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    print("User Sessions API Test")
    print("=" * 60)
    print("\n📌 This test will:")
    print("  • Login with your credentials")
    print("  • Retrieve current session information")
    print("  • Display session details from JWT token")
    print("  • Show session metadata and duration")
    print("\n" + "=" * 60)

    test_sessions()