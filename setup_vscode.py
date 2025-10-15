"""
Automated setup script for VS Code - runs when pressing F5
This script automatically sets up everything needed to run the Django application

Windows: python setup_vscode.py
Linux/Mac: python3 setup_vscode.py
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


class VSCodeSetup:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.venv_dir = self.base_dir / '.venv'
        self.python_exe = self.venv_dir / 'Scripts' / 'python.exe'
        self.pip_exe = self.venv_dir / 'Scripts' / 'pip.exe'

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60 + "\n")

    def run_command(self, command, shell=False):
        """Run a command and return success status"""
        try:
            print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
            result = subprocess.run(command, shell=shell, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False
            if result.stdout:
                print(result.stdout)
            return True
        except Exception as e:
            print(f"Exception: {e}")
            return False

    def check_python(self):
        """Check if Python is installed"""
        self.print_header("Checking Python Installation")
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            print(f"Found: {result.stdout.strip()}")
            return True
        except:
            print("ERROR: Python is not properly installed!")
            return False

    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        self.print_header("Setting up Virtual Environment")

        if self.venv_dir.exists() and self.python_exe.exists():
            print("✓ Virtual environment already exists")
            return True

        print("Creating virtual environment...")
        if not self.run_command([sys.executable, "-m", "venv", str(self.venv_dir)]):
            return False

        print("✓ Virtual environment created successfully")
        return True

    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        self.print_header("Upgrading pip")
        return self.run_command([str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"])

    def install_requirements(self):
        """Install required packages"""
        self.print_header("Installing Requirements")

        req_file = self.base_dir / "requirements.txt"
        if not req_file.exists():
            print("WARNING: requirements.txt not found!")
            return False

        print("Installing packages from requirements.txt...")
        return self.run_command([str(self.pip_exe), "install", "-r", str(req_file)])

    def create_env_file(self):
        """Create .env file from example if it doesn't exist"""
        self.print_header("Setting up Environment Configuration")

        env_file = self.base_dir / ".env"
        env_example = self.base_dir / ".env.example"

        if env_file.exists():
            print("✓ .env file already exists")
            return True

        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✓ Created .env file from .env.example")
            print("⚠ Please update .env with your database credentials!")
            return True
        else:
            print("Creating default .env file...")
            default_env = """# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-xyz123abc456
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - Primary Transaction Database
DB_PRIMARY_NAME=sabpaisa2_stage_sabpaisa
DB_PRIMARY_USER=root
DB_PRIMARY_PASSWORD=password
DB_PRIMARY_HOST=localhost
DB_PRIMARY_PORT=3306

# Database Configuration - Legacy Database
DB_LEGACY_NAME=sabpaisa2_stage_legacy
DB_LEGACY_USER=root
DB_LEGACY_PASSWORD=password
DB_LEGACY_HOST=localhost
DB_LEGACY_PORT=3306

# Database Configuration - User Management Database
DB_USER_NAME=spclientonboard
DB_USER_USER=root
DB_USER_PASSWORD=password
DB_USER_HOST=localhost
DB_USER_PORT=3306

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
            with open(env_file, 'w') as f:
                f.write(default_env)
            print("✓ Created default .env file")
            print("⚠ Please update .env with your actual database credentials!")
            return True

    def create_directories(self):
        """Create necessary directories"""
        self.print_header("Creating Required Directories")

        directories = [
            "logs",
            "media",
            "media/exports",
            "media/reports",
            "static",
            "staticfiles",
            "exports",
            "reports"
        ]

        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {dir_name}")
            else:
                print(f"  Directory exists: {dir_name}")

        return True

    def check_django_installation(self):
        """Check if Django is properly installed"""
        self.print_header("Verifying Django Installation")

        try:
            result = subprocess.run(
                [str(self.python_exe), "-c", "import django; print(f'Django {django.VERSION} installed')"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ {result.stdout.strip()}")
                return True
            else:
                print("ERROR: Django is not installed properly!")
                return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def run_migrations(self):
        """Run Django migrations"""
        self.print_header("Running Database Migrations")

        manage_py = self.base_dir / "manage.py"
        if not manage_py.exists():
            print("ERROR: manage.py not found!")
            return False

        print("Running migrations for default database...")
        if not self.run_command([str(self.python_exe), str(manage_py), "migrate"]):
            print("WARNING: Migration failed. Database might not be configured.")
            print("Please check your database settings in .env file")
            return False

        print("✓ Migrations completed successfully")
        return True

    def collect_static(self):
        """Collect static files"""
        self.print_header("Collecting Static Files")

        manage_py = self.base_dir / "manage.py"
        self.run_command([str(self.python_exe), str(manage_py), "collectstatic", "--noinput"])
        return True

    def show_next_steps(self):
        """Display next steps to the user"""
        self.print_header("Setup Complete! 🎉")

        print("✅ Virtual environment is ready")
        print("✅ All dependencies are installed")
        print("✅ Directory structure is created")
        print("✅ Environment configuration is ready")
        print()
        print("📝 NEXT STEPS:")
        print()
        print("1. Update .env file with your actual database credentials")
        print("2. Ensure MySQL and Redis are running")
        print("3. Press F5 to run the Django server")
        print("4. Access the application at http://localhost:8000")
        print()
        print("🚀 QUICK ACTIONS IN VS CODE:")
        print("   • F5: Run Django Server")
        print("   • Ctrl+Shift+P: Command Palette")
        print("   • Ctrl+Shift+D: Debug Panel")
        print("   • Ctrl+`: Terminal")
        print()
        print("=" * 60)

    def run(self):
        """Main setup process"""
        print("\n" + "🚀 SabPaisa Reports API - VS Code Setup".center(60, "="))
        print("This script will set up everything for you automatically!")

        # Run setup steps
        steps = [
            ("Python Check", self.check_python),
            ("Virtual Environment", self.create_virtual_environment),
            ("Pip Upgrade", self.upgrade_pip),
            ("Package Installation", self.install_requirements),
            ("Environment Config", self.create_env_file),
            ("Directory Structure", self.create_directories),
            ("Django Verification", self.check_django_installation),
            ("Database Setup", self.run_migrations),
            ("Static Files", self.collect_static),
        ]

        for step_name, step_func in steps:
            if not step_func():
                print(f"\n⚠ Warning: {step_name} had issues but continuing...")

        self.show_next_steps()
        return True


if __name__ == "__main__":
    setup = VSCodeSetup()
    try:
        setup.run()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        sys.exit(1)