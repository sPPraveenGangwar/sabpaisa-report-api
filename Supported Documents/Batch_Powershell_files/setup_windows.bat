@echo off
echo ========================================
echo SabPaisa Reports API - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.12.7 from https://www.python.org/downloads/
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Creating .env file from example...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please update it with your configuration.
) else (
    echo .env file already exists.
)

echo.
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "static" mkdir static
if not exist "exports" mkdir exports
if not exist "reports" mkdir reports

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update .env file with your database and service configurations
echo 2. Run migrations: python manage.py migrate
echo 3. Create superuser: python manage.py createsuperuser
echo 4. Run server: python manage.py runserver
echo.
echo To activate virtual environment in the future:
echo   .venv\Scripts\activate.bat
echo.
pause