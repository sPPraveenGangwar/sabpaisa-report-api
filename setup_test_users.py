"""
Script to create test users in the database
Run this with: python setup_test_users.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from datetime import datetime
import hashlib

def create_test_users():
    """Create test users for development"""

    users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@sabpaisa.com',
            'mobile': '9999999999',
            'role_id': 1,  # Admin
            'client_code': None,
            'is_active': 1
        },
        {
            'username': 'merchant1',
            'password': 'merchant123',
            'email': 'merchant1@example.com',
            'mobile': '9876543210',
            'role_id': 2,  # Merchant
            'client_code': 'MERC001',
            'is_active': 1
        },
        {
            'username': 'merchant2',
            'password': 'merchant123',
            'email': 'merchant2@example.com',
            'mobile': '9876543211',
            'role_id': 2,  # Merchant
            'client_code': 'MERC002',
            'is_active': 1
        }
    ]

    with connection.cursor() as cursor:
        # Use the user_management database
        cursor.execute("USE spclientonboard;")

        # Check if roles exist, if not create them
        cursor.execute("SELECT COUNT(*) FROM lookup_role;")
        role_count = cursor.fetchone()[0]

        if role_count == 0:
            print("Creating roles...")
            roles = [
                (1, 'ADMIN', 'Administrator'),
                (2, 'MERCHANT', 'Merchant User'),
                (3, 'ACCOUNT_MANAGER', 'Account Manager'),
                (4, 'BUSINESS_ANALYST', 'Business Analyst')
            ]
            for role_id, role_code, role_name in roles:
                cursor.execute(
                    "INSERT INTO lookup_role (role_id, role_code, role_name) VALUES (%s, %s, %s)",
                    (role_id, role_code, role_name)
                )
            print("Roles created successfully!")

        # Create users
        for user in users:
            # Check if user exists
            cursor.execute(
                "SELECT COUNT(*) FROM login_master WHERE username = %s",
                (user['username'],)
            )
            exists = cursor.fetchone()[0]

            if exists == 0:
                # Hash password with MD5 for compatibility with existing system
                password_hash = hashlib.md5(user['password'].encode()).hexdigest()

                cursor.execute("""
                    INSERT INTO login_master
                    (username, password, email, mobile, role_id, client_code, is_active, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user['username'],
                    password_hash,
                    user['email'],
                    user['mobile'],
                    user['role_id'],
                    user['client_code'],
                    user['is_active'],
                    datetime.now()
                ))
                print(f"✅ Created user: {user['username']} (Password: {user['password']})")
            else:
                print(f"⚠️  User {user['username']} already exists")

        # Also create client entries for merchants
        cursor.execute("USE sabpaisa2_stage_sabpaisa;")

        merchant_clients = [
            {
                'client_code': 'MERC001',
                'client_name': 'Test Merchant 1 Pvt Ltd',
                'client_email': 'merchant1@example.com',
                'client_contact': '9876543210'
            },
            {
                'client_code': 'MERC002',
                'client_name': 'Test Merchant 2 Pvt Ltd',
                'client_email': 'merchant2@example.com',
                'client_contact': '9876543211'
            }
        ]

        for client in merchant_clients:
            cursor.execute(
                "SELECT COUNT(*) FROM client_data_table WHERE client_code = %s",
                (client['client_code'],)
            )
            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute("""
                    INSERT INTO client_data_table
                    (client_code, client_name, client_email, client_contact,
                     active, auth_key, auth_iv, client_user_name, client_pass,
                     failed_ru_url, success_ru_url, push_api_url, client_logo_path)
                    VALUES (%s, %s, %s, %s, 1, 'test_key', 'test_iv', %s, 'password',
                            'http://localhost/fail', 'http://localhost/success',
                            'http://localhost/push', '/logo.png')
                """, (
                    client['client_code'],
                    client['client_name'],
                    client['client_email'],
                    client['client_contact'],
                    client['client_code'].lower()
                ))
                print(f"✅ Created client: {client['client_name']}")
            else:
                print(f"⚠️  Client {client['client_code']} already exists")

    print("\n" + "="*50)
    print("Test users created successfully!")
    print("="*50)
    print("\nYou can now login with:")
    print("  Admin:     username='admin', password='admin123'")
    print("  Merchant1: username='merchant1', password='merchant123'")
    print("  Merchant2: username='merchant2', password='merchant123'")

if __name__ == "__main__":
    try:
        create_test_users()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. MySQL is running")
        print("2. Databases are created")
        print("3. .env file has correct database credentials")