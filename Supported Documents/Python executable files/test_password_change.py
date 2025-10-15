"""
Test script for password change functionality
"""
import requests
import json
import hashlib
import pymysql
from decouple import config

BASE_URL = "http://localhost:8000/api/v1"

def test_password_change():
    """Test password change functionality"""
    print("=" * 60)
    print("Password Change Test")
    print("=" * 60)

    # Step 1: Login with current credentials
    print("\n1. Login with current credentials")
    print("-" * 40)

    username = input("Username (or press Enter to skip): ").strip()
    login_master_id = input("Login Master ID (or press Enter to skip): ").strip()
    old_password = input("Current password: ")

    payload = {"password": old_password}
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
        print(f"\nLogged in as:")
        print(f"  Login Master ID: {user_info.get('login_master_id')}")
        print(f"  Username: {user_info.get('username')}")

        # Step 2: Change password
        print("\n2. Change password")
        print("-" * 40)

        new_password = input("Enter new password (min 6 characters): ")
        confirm_password = input("Confirm new password: ")

        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        change_password_payload = {
            "old_password": old_password,
            "new_password": new_password,
            "confirm_password": confirm_password
        }

        print(f"\nChanging password...")
        change_url = f"{BASE_URL}/auth/change-password/"
        change_response = requests.post(
            change_url,
            headers=headers,
            json=change_password_payload
        )

        print(f"Response status: {change_response.status_code}")
        change_result = change_response.json()
        print(f"Response: {json.dumps(change_result, indent=2)}")

        if change_response.status_code == 200 and change_result.get('success'):
            print("\n✅ Password changed successfully!")

            # Step 3: Verify new password works
            print("\n3. Verify new password by logging in again")
            print("-" * 40)

            # Try to login with new password
            new_login_payload = {"password": new_password}
            if login_master_id:
                new_login_payload["login_master_id"] = login_master_id
            elif username:
                new_login_payload["username"] = username

            print("Attempting login with new password...")
            verify_response = requests.post(login_url, json=new_login_payload)

            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                if verify_data.get('success'):
                    print("✅ New password verified! Login successful with new password.")
                else:
                    print(f"❌ Login with new password failed: {verify_data.get('message')}")
            else:
                print(f"❌ Login with new password failed with status {verify_response.status_code}")

            # Step 4: Check database (optional)
            check_db = input("\nDo you want to check the password in database? (y/n): ")
            if check_db.lower() == 'y':
                check_password_in_db(username or login_master_id, new_password)

        else:
            print(f"\n❌ Password change failed")
            if not change_result.get('success'):
                print(f"Error: {change_result.get('message')}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_password_in_db(identifier, password):
    """Check password directly in database"""
    print("\n4. Database verification")
    print("-" * 40)

    try:
        # Connect to database
        conn = pymysql.connect(
            host=config('DB_USER_HOST', default='localhost'),
            user=config('DB_USER_USER', default='root'),
            password=config('DB_USER_PASSWORD', default=''),
            database=config('DB_USER_NAME', default='spclientonboard'),
            port=int(config('DB_USER_PORT', default='3306'))
        )
        cursor = conn.cursor()

        # Get columns
        cursor.execute("SHOW COLUMNS FROM login_master")
        columns = [col[0] for col in cursor.fetchall()]

        # Find identifier column
        id_columns = ["login_master_id", "username", "user_name", "login_name", "email"]
        id_col = None
        for col in id_columns:
            if col in columns:
                id_col = col
                break

        # Find password column
        password_columns = ["password", "pass", "pwd", "user_password"]
        pwd_col = None
        for col in password_columns:
            if col in columns:
                pwd_col = col
                break

        if not id_col or not pwd_col:
            print("❌ Could not find necessary columns")
            return

        # Get user's password from DB
        query = f"SELECT {pwd_col} FROM login_master WHERE {id_col} = %s"
        cursor.execute(query, [identifier])
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            print(f"Password in DB (first 10 chars): {stored_password[:10]}...")
            print(f"Password length: {len(stored_password)}")

            # Check password format
            md5_password = hashlib.md5(password.encode()).hexdigest()

            if stored_password == password:
                print("✅ Password stored as PLAIN TEXT")
                print("⚠️  Warning: Plain text passwords are not secure!")
            elif stored_password == md5_password:
                print("✅ Password stored as MD5 HASH")
                print(f"MD5 hash: {md5_password}")
            else:
                print("❓ Password format unknown")
                print(f"Expected plain: {password}")
                print(f"Expected MD5: {md5_password}")
                print(f"Actual: {stored_password[:20]}...")
        else:
            print(f"❌ User not found with {id_col} = {identifier}")

        conn.close()

    except Exception as e:
        print(f"❌ Database error: {e}")


def test_password_validation():
    """Test password validation rules"""
    print("\n" + "=" * 60)
    print("Testing Password Validation")
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

    # Test cases
    test_cases = [
        {
            "name": "Password too short",
            "payload": {
                "old_password": password,
                "new_password": "12345",
                "confirm_password": "12345"
            }
        },
        {
            "name": "Passwords don't match",
            "payload": {
                "old_password": password,
                "new_password": "NewPass123",
                "confirm_password": "DifferentPass123"
            }
        },
        {
            "name": "Wrong old password",
            "payload": {
                "old_password": "WrongPassword",
                "new_password": "NewPass123",
                "confirm_password": "NewPass123"
            }
        },
        {
            "name": "Missing old password",
            "payload": {
                "new_password": "NewPass123",
                "confirm_password": "NewPass123"
            }
        },
        {
            "name": "Missing new password",
            "payload": {
                "old_password": password,
                "confirm_password": "NewPass123"
            }
        }
    ]

    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print("-" * 40)

        response = requests.post(
            f"{BASE_URL}/auth/change-password/",
            headers=headers,
            json=test['payload']
        )

        result = response.json()
        if result.get('success'):
            print(f"✅ Unexpected success: {result.get('message')}")
        else:
            print(f"✅ Expected failure: {result.get('message')}")


if __name__ == "__main__":
    print("Password Change Test Tool")
    print("=" * 60)

    while True:
        print("\nOptions:")
        print("1. Test password change")
        print("2. Test password validation")
        print("3. Check password in database")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ")

        if choice == "1":
            test_password_change()
        elif choice == "2":
            test_password_validation()
        elif choice == "3":
            identifier = input("Enter username or login_master_id: ")
            password = input("Enter password to check: ")
            check_password_in_db(identifier, password)
        elif choice == "4":
            break
        else:
            print("Invalid choice")

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)