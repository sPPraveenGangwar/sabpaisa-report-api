@echo off
echo Creating necessary directories for SabPaisa Reports API...
echo ==========================================

REM Try to find Python in virtual environment first
if exist ".venv\Scripts\python.exe" (
    echo Using Python from virtual environment...
    .venv\Scripts\python.exe create_directories.py
) else if exist "venv\Scripts\python.exe" (
    echo Using Python from virtual environment...
    venv\Scripts\python.exe create_directories.py
) else (
    echo Using system Python...
    python create_directories.py
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! All directories created.
    echo You can now run the Django server with F5 in VS Code!
) else (
    echo.
    echo ERROR: Failed to create directories.
    echo Please ensure Python is installed and in your PATH.
)

echo.
pause