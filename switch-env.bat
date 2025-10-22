@echo off
REM ===============================================
REM Environment Switcher Script (Windows)
REM Switches between different environment configurations
REM ===============================================

setlocal

if "%1"=="" (
    echo Usage: %0 ^<environment^>
    echo.
    echo Available environments:
    echo   local  - Local development environment
    echo   dev    - Development server environment (13.127.244.103^)
    echo   stage  - Staging environment
    echo   prod   - Production environment (13.201.46.165^)
    echo.
    echo Example: %0 dev
    exit /b 1
)

set ENV=%1

if not "%ENV%"=="local" if not "%ENV%"=="dev" if not "%ENV%"=="stage" if not "%ENV%"=="prod" (
    echo Error: Invalid environment '%ENV%'
    exit /b 1
)

echo Switching to %ENV% environment...

REM Backend environment
set BACKEND_DIR=sabpaisa-report-api
if exist "%BACKEND_DIR%\.env.%ENV%" (
    copy /Y "%BACKEND_DIR%\.env.%ENV%" "%BACKEND_DIR%\.env" >nul
    echo [OK] Backend environment set to %ENV%
) else (
    echo [ERROR] Backend .env.%ENV% not found
)

REM Frontend environment
set FRONTEND_DIR=sabpaisa-report-ui
if exist "%FRONTEND_DIR%\.env.%ENV%" (
    copy /Y "%FRONTEND_DIR%\.env.%ENV%" "%FRONTEND_DIR%\.env" >nul
    echo [OK] Frontend environment set to %ENV%
) else (
    echo [ERROR] Frontend .env.%ENV% not found
)

echo.
echo Environment switched to: %ENV%
echo Note: Restart your services for changes to take effect

endlocal
