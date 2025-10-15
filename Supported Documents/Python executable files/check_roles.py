"""
Quick script to check what roles exist in lookup_role table
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connections

def check_roles():
    """Check what roles exist in lookup_role table"""
    try:
        with connections['user_management'].cursor() as cursor:
            # Check if table exists
            cursor.execute("SHOW TABLES LIKE 'lookup_role'")
            if not cursor.fetchone():
                print("❌ lookup_role table does not exist!")
                return

            # Get all roles
            cursor.execute("SELECT role_id, role_name FROM lookup_role ORDER BY role_id")
            roles = cursor.fetchall()

            if not roles:
                print("⚠️  No roles found in lookup_role table!")
                return

            print("\n✅ Roles in lookup_role table:")
            print("-" * 50)
            for role_id, role_name in roles:
                print(f"  role_id: {role_id:2d} | role_name: {role_name}")
            print("-" * 50)
            print(f"\nTotal roles: {len(roles)}\n")

            # Check for ADMIN role
            admin_roles = [r for r in roles if 'ADMIN' in r[1].upper()]
            if admin_roles:
                print(f"✅ ADMIN role(s) found:")
                for role_id, role_name in admin_roles:
                    print(f"   - role_id: {role_id}, role_name: '{role_name}'")
            else:
                print("⚠️  No ADMIN role found!")

            # Check for MERCHANT role
            merchant_roles = [r for r in roles if 'MERCHANT' in r[1].upper()]
            if merchant_roles:
                print(f"\n✅ MERCHANT role(s) found:")
                for role_id, role_name in merchant_roles:
                    print(f"   - role_id: {role_id}, role_name: '{role_name}'")
            else:
                print("\n⚠️  No MERCHANT role found!")

    except Exception as e:
        print(f"❌ Error checking roles: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  CHECKING LOOKUP_ROLE TABLE")
    print("="*50)
    check_roles()