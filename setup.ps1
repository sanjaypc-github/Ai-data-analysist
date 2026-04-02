# Quick Setup Script for Windows PowerShell
# Run this to set up and start the Autonomous Data Analyst Agent

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Autonomous Data Analyst Agent - Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found or not running" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and ensure it's running" -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if .env exists, if not copy from example
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created (edit it to add API keys)" -ForegroundColor Green
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Build sandbox image
Write-Host "Building sandbox Docker image..." -ForegroundColor Yellow
Write-Host "(This may take 2-3 minutes on first run)" -ForegroundColor Gray

try {
    docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
    Write-Host "✓ Sandbox image built successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to build sandbox image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ask user if they want to start the application
$startApp = Read-Host "Start the application now? (Y/n)"

if ($startApp -eq "" -or $startApp -eq "Y" -or $startApp -eq "y") {
    Write-Host ""
    Write-Host "Starting application with Docker Compose..." -ForegroundColor Yellow
    Write-Host "(Press Ctrl+C to stop)" -ForegroundColor Gray
    Write-Host ""
    
    docker-compose up --build
} else {
    Write-Host ""
    Write-Host "To start the application later, run:" -ForegroundColor Yellow
    Write-Host "  docker-compose up --build" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access points:" -ForegroundColor Yellow
    Write-Host "  Frontend:  http://localhost:8501" -ForegroundColor Cyan
    Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
}
