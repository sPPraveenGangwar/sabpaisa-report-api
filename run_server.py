#!/usr/bin/env python
"""
Quick server runner - Alternative to manage.py runserver
This can be run directly with F5 in VS Code
"""
import os
import sys
import django
from django.core.management import execute_from_command_line


def main():
    """Run the Django development server"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Setup Django
    django.setup()

    print("\n" + "="*60)
    print("🚀 SabPaisa Reports API Server".center(60))
    print("="*60)
    print("\nStarting Django development server...")
    print("Access the application at: http://localhost:8000")
    print("API Documentation at: http://localhost:8000/api/docs/")
    print("\nPress CTRL+C to stop the server\n")
    print("="*60 + "\n")

    # Run the server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease ensure:")
        print("1. Virtual environment is activated")
        print("2. All dependencies are installed (pip install -r requirements.txt)")
        print("3. Database is configured in .env file")
        print("4. Migrations are run (python manage.py migrate)")
        sys.exit(1)