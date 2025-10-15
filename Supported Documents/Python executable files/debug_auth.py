"""
Debug script to check database structure and authentication
"""
import os
import sys
from pathlib import Path
import pymysql
from decouple import config
import hashlib

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def check_database_structure():
    """Check the login_master table structure"""
    print("=" * 60)
    print("Database Structure Check")
    print("=" * 60)

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

        # Check if login_master table exists
        cursor.execute("SHOW TABLES LIKE 'login_master'")
        if not cursor.fetchone():
            print("❌ login_master table does not exist!")
            return False

        print("✅ login_master table exists")

        # Get column information
        cursor.execute("SHOW COLUMNS FROM login_master")
        columns = cursor.fetchall()

        print("\n📋 Table Structure:")
        print("-" * 40)
        print(f"{'Column Name':<20} {'Type':<20} {'Null':<6} {'Key':<6}")
        print("-" * 40)

        column_names = []
        for col in columns:
            column_names.append(col[0])
            print(f"{col[0]:<20} {col[1]:<20} {col[2]:<6} {col[3]:<6}")

        print("\n🔍 Key Columns Check:")
        print("-" * 40)

        # Check for login_master_id
        if 'login_master_id' in column_names:
            print("✅ login_master_id column exists")
        else:
            print("❌ login_master_id column NOT found")

        # Check for username columns
        username_cols = ['username', 'user_name', 'login_name', 'email', 'user_id']
        found_username = None
        for col in username_cols:
            if col in column_names:
                print(f"✅ {col} column exists (can be used for authentication)")
                found_username = col
                break

        if not found_username:
            print("❌ No username column found!")

        # Check for password columns
        password_cols = ['password', 'pass', 'pwd', 'user_password']
        found_password = None
        for col in password_cols:
            if col in column_names:
                print(f"✅ {col} column exists (password field)")
                found_password = col
                break

        if not found_password:
            print("❌ No password column found!")

        # Get sample data (without sensitive info)
        print("\n📊 Sample Data:")
        print("-" * 40)

        # Get count
        cursor.execute("SELECT COUNT(*) FROM login_master")
        count = cursor.fetchone()[0]
        print(f"Total records: {count}")

        if count > 0 and found_username and found_password:
            # Get first few records (hiding passwords)
            query = f"SELECT "

            # Select specific columns
            select_cols = []
            if 'login_master_id' in column_names:
                select_cols.append('login_master_id')
            if found_username:
                select_cols.append(found_username)
            if 'email' in column_names:
                select_cols.append('email')
            if 'role_id' in column_names:
                select_cols.append('role_id')

            query += ", ".join(select_cols) + f", LENGTH({found_password}) as pwd_length"
            query += " FROM login_master LIMIT 3"

            cursor.execute(query)
            rows = cursor.fetchall()

            print(f"\nFirst 3 records (password hidden):")
            for row in rows:
                print(f"  {row}")

        # Check password format
        if found_password:
            print("\n🔐 Password Format Check:")
            print("-" * 40)
            cursor.execute(f"SELECT {found_password} FROM login_master LIMIT 1")
            sample_pwd = cursor.fetchone()
            if sample_pwd and sample_pwd[0]:
                pwd = sample_pwd[0]
                pwd_len = len(pwd)
                print(f"Password length: {pwd_len} characters")

                # Check if it looks like MD5 (32 characters hex)
                if pwd_len == 32 and all(c in '0123456789abcdef' for c in pwd.lower()):
                    print("✅ Passwords appear to be MD5 hashed")
                elif pwd_len > 50:
                    print("🔒 Passwords might be bcrypt or another secure hash")
                else:
                    print("⚠️  Passwords might be plain text or simple hash")

        conn.close()
        return True

    except pymysql.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_authentication():
    """Test authentication with sample credentials"""
    print("\n" + "=" * 60)
    print("Authentication Test")
    print("=" * 60)

    try:
        conn = MySQLdb.connect(
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

        # Find auth and password columns
        username_columns = ["login_master_id", "username", "user_name", "login_name", "email", "user_id"]
        password_columns = ["password", "pass", "pwd", "user_password"]

        username_col = None
        password_col = None

        for col in username_columns:
            if col in columns:
                username_col = col
                break

        for col in password_columns:
            if col in columns:
                password_col = col
                break

        if not username_col or not password_col:
            print("❌ Cannot find username/password columns")
            return

        print(f"Using columns: {username_col} for auth, {password_col} for password")

        # Get user input
        print("\n🔑 Enter credentials to test:")
        auth_id = input(f"Enter {username_col}: ")
        password = input("Enter password: ")

        # Test plain password
        query = f"SELECT * FROM login_master WHERE {username_col} = %s AND {password_col} = %s"
        cursor.execute(query, [auth_id, password])
        user = cursor.fetchone()

        if user:
            print("✅ Authentication successful with plain password!")
            return

        # Test MD5
        md5_password = hashlib.md5(password.encode()).hexdigest()
        cursor.execute(query, [auth_id, md5_password])
        user = cursor.fetchone()

        if user:
            print("✅ Authentication successful with MD5 hash!")
            print(f"MD5 hash used: {md5_password}")
            return

        # Check if user exists
        cursor.execute(f"SELECT * FROM login_master WHERE {username_col} = %s", [auth_id])
        user = cursor.fetchone()

        if user:
            print(f"⚠️  User exists but password doesn't match")
            print(f"Tried plain: {password}")
            print(f"Tried MD5: {md5_password}")

            # Show actual password (partially hidden)
            pwd_index = columns.index(password_col)
            actual_pwd = user[pwd_index]
            if actual_pwd:
                print(f"Actual password in DB (first 10 chars): {actual_pwd[:10]}...")
                print(f"Actual password length: {len(actual_pwd)}")
        else:
            print(f"❌ User not found with {username_col} = {auth_id}")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("SabPaisa API - Authentication Debug Tool")
    print("=" * 60)

    # Check database structure
    if check_database_structure():
        # Test authentication
        test_authentication()
    else:
        print("\n❌ Cannot proceed with authentication test due to database issues")

    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)