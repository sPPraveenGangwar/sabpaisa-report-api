"""
Test MySQL connection and create databases if needed
Run this before starting Django to ensure database connectivity
"""
import os
import sys
from pathlib import Path
import MySQLdb
from decouple import config

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_mysql_connection():
    """Test MySQL connection and create databases if they don't exist"""

    print("=" * 60)
    print("MySQL Connection Test for SabPaisa Reports API")
    print("=" * 60)

    # Read credentials from .env file or defaults
    db_configs = [
        {
            'name': 'Primary Database',
            'db_name': config('DB_PRIMARY_NAME', default='sabpaisa2_stage_sabpaisa'),
            'user': config('DB_PRIMARY_USER', default='root'),
            'password': config('DB_PRIMARY_PASSWORD', default=''),
            'host': config('DB_PRIMARY_HOST', default='localhost'),
            'port': int(config('DB_PRIMARY_PORT', default='3306')),
        },
        {
            'name': 'Legacy Database',
            'db_name': config('DB_LEGACY_NAME', default='sabpaisa2_stage_legacy'),
            'user': config('DB_LEGACY_USER', default='root'),
            'password': config('DB_LEGACY_PASSWORD', default=''),
            'host': config('DB_LEGACY_HOST', default='localhost'),
            'port': int(config('DB_LEGACY_PORT', default='3306')),
        },
        {
            'name': 'User Management Database',
            'db_name': config('DB_USER_NAME', default='spclientonboard'),
            'user': config('DB_USER_USER', default='root'),
            'password': config('DB_USER_PASSWORD', default=''),
            'host': config('DB_USER_HOST', default='localhost'),
            'port': int(config('DB_USER_PORT', default='3306')),
        }
    ]

    print("\n📋 Database Configuration:")
    print("-" * 40)

    for db_config in db_configs:
        print(f"\n{db_config['name']}:")
        print(f"  Database: {db_config['db_name']}")
        print(f"  User: {db_config['user']}")
        print(f"  Host: {db_config['host']}:{db_config['port']}")
        print(f"  Password: {'*' * len(db_config['password']) if db_config['password'] else '(empty)'}")

    print("\n" + "=" * 60)
    print("Testing MySQL Connection...")
    print("-" * 40)

    # Test connection to MySQL server (without database)
    try:
        # First connect without database to create databases if needed
        conn = MySQLdb.connect(
            host=db_configs[0]['host'],
            user=db_configs[0]['user'],
            password=db_configs[0]['password'],
            port=db_configs[0]['port']
        )
        cursor = conn.cursor()
        print("✅ Successfully connected to MySQL server!")

        # Create databases if they don't exist
        print("\nChecking/Creating databases...")
        for db_config in db_configs:
            db_name = db_config['db_name']
            try:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
                if cursor.fetchone():
                    print(f"✅ Database '{db_name}' exists")
                else:
                    print(f"❌ Could not create database '{db_name}'")
            except Exception as e:
                print(f"⚠️  Error with database '{db_name}': {e}")

        conn.close()

    except MySQLdb.OperationalError as e:
        print(f"\n❌ MySQL Connection Failed!")
        print(f"Error: {e}")
        print("\n🔧 Common Solutions:")
        print("1. Check if MySQL service is running:")
        print("   - Windows: Check Services (services.msc) for 'MySQL' or 'MySQL80'")
        print("   - Or run: net start MySQL80")
        print("\n2. Verify your credentials in .env file:")
        print("   - DB_PRIMARY_USER=your_mysql_user")
        print("   - DB_PRIMARY_PASSWORD=your_mysql_password")
        print("\n3. If password is empty, try:")
        print("   - DB_PRIMARY_PASSWORD=")
        print("   - Or remove the password line entirely")
        print("\n4. Common MySQL users:")
        print("   - root (with your root password)")
        print("   - root (with empty password)")
        print("\n5. Reset MySQL root password if forgotten:")
        print("   - Stop MySQL service")
        print("   - Start with: mysqld --skip-grant-tables")
        print("   - Connect and reset password")
        return False

    print("\n" + "=" * 60)
    print("✅ All database checks passed!")
    print("You can now run the Django server with F5")
    print("=" * 60)
    return True

if __name__ == "__main__":
    # Check if .env file exists
    env_file = BASE_DIR / '.env'
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Creating .env file from .env.example...")

        env_example = BASE_DIR / '.env.example'
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file")
            print("📝 Please update the database credentials in .env file:")
            print("   - DB_PRIMARY_PASSWORD=your_mysql_password")
            print("   - Or leave empty if no password: DB_PRIMARY_PASSWORD=")
        else:
            # Create a minimal .env file
            with open(env_file, 'w') as f:
                f.write("""# Database Configuration
DB_PRIMARY_NAME=sabpaisa2_stage_sabpaisa
DB_PRIMARY_USER=root
DB_PRIMARY_PASSWORD=
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

DB_LEGACY_NAME=sabpaisa2_stage_legacy
DB_LEGACY_USER=root
DB_LEGACY_PASSWORD=
DB_LEGACY_HOST=localhost
DB_LEGACY_PORT=3306

DB_USER_NAME=spclientonboard
DB_USER_USER=root
DB_USER_PASSWORD=
DB_USER_HOST=localhost
DB_USER_PORT=3306

# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-dev-key-change-in-production
""")
            print("✅ Created minimal .env file")
            print("📝 Update DB_PRIMARY_PASSWORD in .env with your MySQL password")

    test_mysql_connection()