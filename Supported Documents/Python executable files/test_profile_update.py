"""
Test script for profile update functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_profile_update():
    """Test profile update functionality"""
    print("=" * 60)
    print("Profile Update Test")
    print("=" * 60)

    # Step 1: Login first
    print("\n1. Login to get access token")
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
        print(f"\nCurrent user info:")
        print(f"  Login Master ID: {user_info.get('login_master_id')}")
        print(f"  Username: {user_info.get('username')}")
        print(f"  Email: {user_info.get('email')}")
        print(f"  Name: {user_info.get('name')}")

        # Step 2: Get current profile
        print("\n2. Get current profile")
        print("-" * 40)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        profile_url = f"{BASE_URL}/auth/profile/"
        profile_response = requests.get(profile_url, headers=headers)

        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            if profile_data.get('success'):
                print("✅ Current profile:")
                current_profile = profile_data.get('data', {})
                for key, value in current_profile.items():
                    if value:  # Only show non-empty fields
                        print(f"  {key}: {value}")
        else:
            print(f"⚠️  Could not fetch current profile (status {profile_response.status_code})")

        # Step 3: Update profile
        print("\n3. Update profile")
        print("-" * 40)
        print("\nEnter new values (press Enter to skip):")

        update_data = {}

        # Collect update data
        new_email = input("New email: ").strip()
        if new_email:
            update_data['email'] = new_email

        new_name = input("New name: ").strip()
        if new_name:
            update_data['name'] = new_name

        new_mobile = input("New mobile: ").strip()
        if new_mobile:
            update_data['mobile_number'] = new_mobile

        new_address = input("New address: ").strip()
        if new_address:
            update_data['address'] = new_address

        new_city = input("New city: ").strip()
        if new_city:
            update_data['city'] = new_city

        if not update_data:
            print("⚠️  No data to update")
            return

        print(f"\nUpdating with: {json.dumps(update_data, indent=2)}")

        # Make PUT request
        update_response = requests.put(
            profile_url,
            headers=headers,
            json=update_data
        )

        print(f"\nResponse status: {update_response.status_code}")
        update_result = update_response.json()
        print(f"Response: {json.dumps(update_result, indent=2)}")

        if update_response.status_code == 200 and update_result.get('success'):
            print("\n✅ Profile updated successfully!")

            # Show updated data
            if 'data' in update_result:
                print("\nUpdated profile:")
                for key, value in update_result['data'].items():
                    if value:  # Only show non-empty fields
                        print(f"  {key}: {value}")
        else:
            print(f"\n❌ Profile update failed")
            if 'allowed_fields' in update_result:
                print(f"Allowed fields for update: {update_result['allowed_fields']}")

        # Step 4: Verify update by fetching profile again
        print("\n4. Verify update")
        print("-" * 40)

        verify_response = requests.get(profile_url, headers=headers)
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data.get('success'):
                print("✅ Profile after update:")
                updated_profile = verify_data.get('data', {})
                for key, value in updated_profile.items():
                    if value:  # Only show non-empty fields
                        print(f"  {key}: {value}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_invalid_fields():
    """Test updating with invalid fields"""
    print("\n" + "=" * 60)
    print("Testing Invalid Field Update")
    print("=" * 60)

    # Need to login first
    print("\nQuick login for testing...")
    username = input("Username: ")
    password = input("Password: ")

    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": username, "password": password}
    )

    if login_response.status_code != 200:
        print("❌ Login failed")
        return

    access_token = login_response.json()['data']['access']
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Try to update protected fields
    print("\nTrying to update protected fields...")
    invalid_update = {
        "login_master_id": "999",  # Should not be allowed
        "role_id": "1",  # Should not be allowed
        "password": "newpassword",  # Should not be allowed
        "email": "test@example.com"  # This should work
    }

    response = requests.put(
        f"{BASE_URL}/auth/profile/",
        headers=headers,
        json=invalid_update
    )

    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    if result.get('success'):
        print("\n✅ Only allowed fields were updated")
    else:
        print(f"\n⚠️  {result.get('message')}")
        if 'allowed_fields' in result:
            print(f"Allowed fields: {result['allowed_fields']}")


if __name__ == "__main__":
    print("Profile Update Test Tool")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Test profile update")
        print("2. Test invalid field update")
        print("3. Exit")

        choice = input("\nEnter choice (1-3): ")

        if choice == "1":
            test_profile_update()
        elif choice == "2":
            test_invalid_fields()
        elif choice == "3":
            break
        else:
            print("Invalid choice")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)