"""
Safe server runner that ensures all directories exist before starting Django.
This script is called by VS Code when pressing F5.

Windows: python run_server_safe.py
Linux/Mac: python3 run_server_safe.py
"""
import os
import sys
import subprocess
from pathlib import Path


def create_directories():
    """Create all necessary directories before starting Django"""
    base_dir = Path(__file__).resolve().parent

    directories = [
        'logs',
        'media',
        'media/exports',
        'media/reports',
        'static',
        'staticfiles',
        'exports',
        'reports',
    ]

    print("Ensuring directories exist...")
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create log file
    log_file = base_dir / 'logs' / 'django.log'
    if not log_file.exists():
        log_file.touch()

    print("✓ All directories ready")


def main():
    """Main entry point"""
    # Create directories first
    create_directories()

    # Now run Django server
    base_dir = Path(__file__).resolve().parent
    manage_py = base_dir / "manage.py"

    # Set environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Run the Django development server
    print("\nStarting Django development server...")
    print("=" * 50)

    try:
        # Use the Python interpreter from the virtual environment
        python_exe = sys.executable
        subprocess.run([
            python_exe,
            str(manage_py),
            "runserver",
            "0.0.0.0:8000",
            "--noreload"
        ])
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()