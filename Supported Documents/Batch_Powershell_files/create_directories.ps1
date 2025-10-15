# PowerShell script to create necessary directories for SabPaisa Reports API
Write-Host "Creating necessary directories for SabPaisa Reports API..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Get the script directory
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# List of directories to create
$directories = @(
    "logs",
    "media",
    "media\exports",
    "media\reports",
    "static",
    "staticfiles",
    "exports",
    "reports"
)

# Create each directory
foreach ($dir in $directories) {
    $fullPath = Join-Path $BaseDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Exists: $dir" -ForegroundColor Yellow
    }
}

# Create the log file
$logFile = Join-Path $BaseDir "logs\django.log"
if (-not (Test-Path $logFile)) {
    New-Item -ItemType File -Path $logFile -Force | Out-Null
    Write-Host "✓ Created: logs\django.log" -ForegroundColor Green
} else {
    Write-Host "  Exists: logs\django.log" -ForegroundColor Yellow
}

Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "All directories created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the Django server with F5 in VS Code!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")