"""
Test script for individual session operations
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_session_detail():
    """Test individual session operations"""
    print("=" * 60)
    print("Session Detail Operations Test")
    print("=" * 60)

    # Step 1: Login to get access token
    print("\n1. Login to get access token")
    print("-" * 40)

    username = input("Username or Login Master ID: ")
    password = input("Password: ")

    # Prepare login payload
    payload = {"password": password}
    if username.isdigit():
        payload["login_master_id"] = username
    else:
        payload["username"] = username

    # Login
    login_url = f"{BASE_URL}/auth/login/"
    try:
        response = requests.post(login_url, json=payload)

        if response.status_code != 200:
            print(f"❌ Login failed with status {response.status_code}")
            return

        data = response.json()
        if not data.get('success'):
            print(f"❌ Login failed: {data.get('message')}")
            return

        access_token = data['data']['access']
        user_info = data['data']['user']

        print("✅ Login successful!")
        print(f"User: {user_info.get('username')} (ID: {user_info.get('login_master_id')})")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Step 2: Get all sessions to find session ID
        print("\n2. Get current session ID")
        print("-" * 40)

        sessions_response = requests.get(f"{BASE_URL}/auth/sessions/", headers=headers)
        if sessions_response.status_code != 200:
            print("❌ Failed to get sessions")
            return

        sessions_data = sessions_response.json()
        if not sessions_data.get('data'):
            print("❌ No active sessions found")
            return

        current_session = sessions_data['data'][0]
        session_id = current_session.get('session_id')
        print(f"✅ Current session ID: {session_id}")

        # Step 3: Test GET session detail
        print("\n3. GET session details")
        print("-" * 40)

        detail_url = f"{BASE_URL}/auth/sessions/{session_id}/"
        print(f"GET {detail_url}")

        detail_response = requests.get(detail_url, headers=headers)
        print(f"Status: {detail_response.status_code}")

        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            if detail_data.get('success'):
                print("✅ Session details retrieved!")
                session = detail_data.get('data', {})
                print(f"\nSession Details:")
                print(f"  Session ID: {session.get('session_id')}")
                print(f"  User: {session.get('username')}")
                print(f"  Login Master ID: {session.get('login_master_id')}")
                print(f"  Created: {session.get('created_at')}")
                print(f"  Expires: {session.get('expires_at')}")
                print(f"  Remaining: {session.get('remaining_readable')}")
                print(f"  Is Current: {session.get('is_current')}")
                print(f"  Is Active: {session.get('is_active')}")
        else:
            print(f"❌ Failed to get session details: {detail_response.json()}")

        # Step 4: Test POST action (terminate)
        print("\n4. Test session actions")
        print("-" * 40)

        test_terminate = input("\nTest session termination? (y/n): ")
        if test_terminate.lower() == 'y':
            # Create a second session first
            print("\nCreating a second session for testing...")
            response2 = requests.post(login_url, json=payload)
            if response2.status_code == 200:
                data2 = response2.json()
                if data2.get('success'):
                    access_token2 = data2['data']['access']
                    headers2 = {
                        "Authorization": f"Bearer {access_token2}",
                        "Content-Type": "application/json"
                    }

                    # Get the new session ID
                    sessions_response2 = requests.get(f"{BASE_URL}/auth/sessions/", headers=headers2)
                    if sessions_response2.status_code == 200:
                        sessions_data2 = sessions_response2.json()
                        if sessions_data2.get('data'):
                            session2 = sessions_data2['data'][0]
                            session_id2 = session2.get('session_id')
                            print(f"✅ Second session created: {session_id2}")

                            # Try to terminate the second session using the first token
                            print(f"\nTerminating session {session_id2}...")
                            terminate_payload = {"action": "terminate"}

                            terminate_response = requests.post(
                                f"{BASE_URL}/auth/sessions/{session_id2}/",
                                headers=headers,
                                json=terminate_payload
                            )

                            print(f"Status: {terminate_response.status_code}")
                            terminate_data = terminate_response.json()
                            print(f"Response: {json.dumps(terminate_data, indent=2)}")

                            # Test DELETE method
                            print(f"\nTesting DELETE method on current session...")
                            delete_response = requests.delete(
                                f"{BASE_URL}/auth/sessions/{session_id}/",
                                headers=headers
                            )
                            print(f"DELETE Status: {delete_response.status_code}")
                            print(f"Response: {json.dumps(delete_response.json(), indent=2)}")

        # Step 5: Test invalid session ID
        print("\n5. Test invalid session ID")
        print("-" * 40)

        invalid_id = "invalid_session_id_12345"
        invalid_response = requests.get(
            f"{BASE_URL}/auth/sessions/{invalid_id}/",
            headers=headers
        )
        print(f"GET /sessions/{invalid_id}/")
        print(f"Status: {invalid_response.status_code}")
        if invalid_response.status_code == 404:
            print("✅ Correctly returned 404 for invalid session")
        else:
            print(f"Response: {invalid_response.json()}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    print("Session Detail Operations Test")
    print("=" * 60)
    print("\n📌 This test will:")
    print("  • Get details of a specific session")
    print("  • Test session termination")
    print("  • Test DELETE method")
    print("  • Test invalid session IDs")
    print("\n" + "=" * 60)

    test_session_detail()