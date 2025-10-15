# Redis Installation Script for Windows
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Redis Installation for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create Redis directory
$redisDir = "C:\Redis"
Write-Host "Step 1: Creating Redis directory..." -ForegroundColor Yellow

if (!(Test-Path $redisDir)) {
    New-Item -ItemType Directory -Path $redisDir -Force | Out-Null
    Write-Host "✓ Created $redisDir" -ForegroundColor Green
} else {
    Write-Host "✓ $redisDir already exists" -ForegroundColor Green
}

# Download Redis
Write-Host ""
Write-Host "Step 2: Downloading Redis..." -ForegroundColor Yellow
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
$zipFile = "$redisDir\Redis.zip"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($redisUrl, $zipFile)
    Write-Host "✓ Downloaded Redis" -ForegroundColor Green
} catch {
    Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually:" -ForegroundColor Yellow
    Write-Host "1. Open: $redisUrl"
    Write-Host "2. Save to: $zipFile"
    Write-Host "3. Run this script again"
    exit
}

# Extract Redis
Write-Host ""
Write-Host "Step 3: Extracting Redis..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipFile, $redisDir)
    Remove-Item $zipFile -Force
    Write-Host "✓ Extracted Redis" -ForegroundColor Green
} catch {
    Write-Host "⚠ Extraction failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Please extract $zipFile manually to $redisDir"
}

# Add to PATH
Write-Host ""
Write-Host "Step 4: Adding Redis to PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$redisDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$redisDir", "User")
    $env:Path = "$env:Path;$redisDir"
    Write-Host "✓ Added Redis to PATH" -ForegroundColor Green
} else {
    Write-Host "✓ Redis already in PATH" -ForegroundColor Green
}

# Create Windows Service (optional)
Write-Host ""
Write-Host "Step 5: Installing Redis as Windows Service..." -ForegroundColor Yellow
try {
    $serviceName = "Redis"
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

    if ($existingService) {
        Write-Host "✓ Redis service already exists" -ForegroundColor Green
    } else {
        & "$redisDir\redis-server.exe" --service-install "$redisDir\redis.windows.conf" --loglevel verbose
        Write-Host "✓ Redis service installed" -ForegroundColor Green
    }

    # Start service
    Start-Service Redis -ErrorAction SilentlyContinue
    Write-Host "✓ Redis service started" -ForegroundColor Green
} catch {
    Write-Host "⚠ Service installation failed (this is OK)" -ForegroundColor Yellow
    Write-Host "  You can start Redis manually with: redis-server" -ForegroundColor Yellow
}

# Test Redis
Write-Host ""
Write-Host "Step 6: Testing Redis..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $redisCliPath = "$redisDir\redis-cli.exe"
    if (Test-Path $redisCliPath) {
        $result = & $redisCliPath ping 2>$null
        if ($result -eq "PONG") {
            Write-Host "✓ Redis is running!" -ForegroundColor Green
        } else {
            Write-Host "⚠ Redis not responding, starting manually..." -ForegroundColor Yellow
            Start-Process -FilePath "$redisDir\redis-server.exe" -WindowStyle Hidden
            Start-Sleep -Seconds 2
            $result = & $redisCliPath ping 2>$null
            if ($result -eq "PONG") {
                Write-Host "✓ Redis is now running!" -ForegroundColor Green
            }
        }
    }
} catch {
    Write-Host "⚠ Could not test Redis connection" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Redis installed at: $redisDir" -ForegroundColor White
Write-Host ""
Write-Host "To start Redis manually:" -ForegroundColor Yellow
Write-Host "  redis-server" -ForegroundColor White
Write-Host ""
Write-Host "To test Redis:" -ForegroundColor Yellow
Write-Host "  redis-cli ping" -ForegroundColor White
Write-Host "  (Should return: PONG)" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Close and reopen PowerShell/VS Code" -ForegroundColor White
Write-Host "  2. Press F5 in VS Code to start Django" -ForegroundColor White
Write-Host ""
