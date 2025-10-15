# Simple Redis Installation for Windows
Write-Host "Installing Redis for Windows..." -ForegroundColor Cyan

# Create directory
$redisDir = "C:\Redis"
if (!(Test-Path $redisDir)) {
    New-Item -ItemType Directory -Path $redisDir -Force | Out-Null
}

# Download Redis
$url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
$zip = "$redisDir\Redis.zip"

Write-Host "Downloading Redis..." -ForegroundColor Yellow
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Extracting..." -ForegroundColor Yellow
Expand-Archive -Path $zip -DestinationPath $redisDir -Force
Remove-Item $zip

# Add to PATH
$path = [Environment]::GetEnvironmentVariable("Path", "User")
if ($path -notlike "*$redisDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$path;$redisDir", "User")
    $env:Path += ";$redisDir"
}

Write-Host "Starting Redis..." -ForegroundColor Yellow
Start-Process -FilePath "$redisDir\redis-server.exe" -WindowStyle Minimized

Start-Sleep -Seconds 3

# Test
$test = & "$redisDir\redis-cli.exe" ping 2>$null
if ($test -eq "PONG") {
    Write-Host ""
    Write-Host "SUCCESS! Redis is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now you can:" -ForegroundColor Yellow
    Write-Host "1. Close and reopen VS Code" -ForegroundColor White
    Write-Host "2. Press F5 to start Django" -ForegroundColor White
} else {
    Write-Host "Warning: Redis may not be running properly" -ForegroundColor Yellow
}
