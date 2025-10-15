"""
Create necessary directories for the project
Run this to fix the missing logs directory error

Windows: python create_directories.py
Linux/Mac: python3 create_directories.py
"""
import os
import sys
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# List of directories to create
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

print("Creating necessary directories...")
print("-" * 40)

for dir_name in directories:
    dir_path = BASE_DIR / dir_name
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_name}")
    else:
        print(f"  Exists: {dir_name}")

# Create an empty log file to ensure it exists
log_file = BASE_DIR / 'logs' / 'django.log'
if not log_file.exists():
    log_file.touch()
    print(f"✓ Created: logs/django.log")
else:
    print(f"  Exists: logs/django.log")

print("-" * 40)
print("All directories created successfully!")
print("\nYou can now run the Django server!")