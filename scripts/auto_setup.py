#!/usr/bin/env python3
"""
Automatic setup script for SabPaisa Reports API
Runs before Django server starts - installs dependencies, starts Redis, etc.
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_command(command, shell=True, check=True, capture_output=False):
    """Run a shell command"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check,
                                    capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=shell, check=check)
            return True
    except subprocess.CalledProcessError as e:
        return False

def check_python_version():
    """Check Python version"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    print_info("Checking Python dependencies...")

    requirements_file = Path(__file__).parent.parent / 'requirements.txt'

    if not requirements_file.exists():
        print_warning("requirements.txt not found, skipping dependency installation")
        return True

    try:
        # Check if dependencies are already installed
        print_info("Installing/updating dependencies (this may take a moment)...")

        cmd = f'{sys.executable} -m pip install -q -r "{requirements_file}"'
        result = run_command(cmd, capture_output=True)

        if result or result is None:
            print_success("All Python dependencies installed/verified")
            return True
        else:
            print_warning("Some dependencies may need manual installation")
            return True
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False

def check_redis():
    """Check if Redis is installed and running"""
    print_info("Checking Redis...")

    # Try to import redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=2)
        r.ping()
        print_success("Redis is running on localhost:6379")
        return True
    except ImportError:
        print_warning("redis-py not installed, installing...")
        run_command(f'{sys.executable} -m pip install -q redis django-redis hiredis')
        return check_redis()
    except Exception as e:
        print_warning(f"Redis not accessible: {e}")
        return start_redis()

def start_redis():
    """Attempt to start Redis server"""
    print_info("Attempting to start Redis...")

    system = platform.system()

    if system == "Windows":
        # Check if Redis is installed via Memurai or Redis for Windows
        redis_paths = [
            r"C:\Program Files\Redis\redis-server.exe",
            r"C:\Program Files\Memurai\memurai.exe",
            r"C:\Redis\redis-server.exe",
        ]

        for redis_path in redis_paths:
            if os.path.exists(redis_path):
                print_info(f"Starting Redis from {redis_path}")
                try:
                    subprocess.Popen([redis_path],
                                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
                    time.sleep(2)
                    return check_redis()
                except Exception as e:
                    print_warning(f"Failed to start Redis: {e}")

        print_warning("Redis not found. Downloading Redis...")
        print_info("Please install Redis manually:")
        print_info("  Option 1: Download from https://github.com/microsoftarchive/redis/releases")
        print_info("  Option 2: Install Memurai from https://www.memurai.com/")
        print_info("")
        print_warning("Application will use fallback caching (slower)")
        return False

    elif system == "Linux":
        # Try to start Redis on Linux
        commands = [
            "sudo systemctl start redis",
            "sudo service redis-server start",
            "redis-server --daemonize yes"
        ]

        for cmd in commands:
            print_info(f"Trying: {cmd}")
            if run_command(cmd, check=False):
                time.sleep(2)
                try:
                    import redis
                    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=2)
                    r.ping()
                    print_success("Redis started successfully")
                    return True
                except:
                    continue

        print_warning("Could not start Redis. Install with: sudo apt install redis-server")
        print_warning("Application will use fallback caching (slower)")
        return False

    else:
        print_warning(f"Unsupported platform: {system}")
        return False

def check_env_file():
    """Check if .env file exists"""
    print_info("Checking .env configuration...")

    env_file = Path(__file__).parent.parent / '.env'
    env_example = Path(__file__).parent.parent / '.env.example'

    if env_file.exists():
        print_success(".env file found")
        return True

    if env_example.exists():
        print_warning(".env file not found, copying from .env.example")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print_success(".env file created from template")
            return True
        except Exception as e:
            print_error(f"Failed to create .env: {e}")
            return False

    print_warning(".env file not found (optional)")
    return True

def check_database():
    """Check database connection"""
    print_info("Checking database connection...")

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        import django
        django.setup()

        from django.db import connection
        connection.ensure_connection()

        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        print_info("Make sure MySQL is running and credentials in .env are correct")
        return False

def run_migrations():
    """Run Django migrations if needed"""
    print_info("Checking migrations...")

    try:
        result = run_command(
            f'{sys.executable} manage.py showmigrations --plan',
            capture_output=True
        )

        if result and '[ ]' in result:
            print_warning("Unapplied migrations found, running migrations...")
            run_command(f'{sys.executable} manage.py migrate --noinput')
            print_success("Migrations completed")
        else:
            print_success("All migrations up to date")
        return True
    except Exception as e:
        print_warning(f"Migration check skipped: {e}")
        return True

def main():
    """Main setup function"""
    print_header("SabPaisa Reports API - Automatic Setup")

    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print_info(f"Working directory: {project_root}")

    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Python Dependencies", install_dependencies),
        ("Redis Cache", check_redis),
        ("Environment Config", check_env_file),
        ("Database Connection", check_database),
        ("Database Migrations", run_migrations),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error in {name}: {e}")
            results.append((name, False))

    # Print summary
    print_header("Setup Summary")

    for name, result in results:
        if result:
            print_success(f"{name}: OK")
        else:
            print_warning(f"{name}: WARNING (non-critical)")

    # Check if critical components are ready
    critical_failures = [name for name, result in results if not result and name in ["Python Version", "Database Connection"]]

    if critical_failures:
        print_error(f"\nCritical setup failures: {', '.join(critical_failures)}")
        print_error("Please fix these issues before running the server")
        sys.exit(1)

    print_success("\n✓ Setup complete! Starting Django server...\n")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
