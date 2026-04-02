# Setup Script for Python 3.12 Virtual Environment
# This creates a venv with Python 3.12 without affecting your system Python 3.8

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ADA Agent Setup - Python 3.12 venv" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check available Python versions
Write-Host "Checking Python installations..." -ForegroundColor Yellow
try {
    $pythonVersions = py -0 2>&1
    Write-Host $pythonVersions -ForegroundColor Gray
} catch {
    Write-Host "Python launcher not found" -ForegroundColor Red
}

Write-Host ""

# Check if Python 3.12 is available
Write-Host "Checking for Python 3.12..." -ForegroundColor Yellow
try {
    $py312Version = py -3.12 --version 2>&1
    Write-Host "✓ Found: $py312Version" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 3.12 not found" -ForegroundColor Red
    Write-Host "Please install Python 3.12 from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create virtual environment with Python 3.12
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
    $recreate = Read-Host "Recreate it? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "Removing existing venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
        Write-Host "Creating new virtual environment with Python 3.12..." -ForegroundColor Yellow
        py -3.12 -m venv venv
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    }
} else {
    Write-Host "Creating virtual environment with Python 3.12..." -ForegroundColor Yellow
    py -3.12 -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Verify Python version
$venvPython = python --version
Write-Host "✓ Active Python: $venvPython" -ForegroundColor Green

Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

Write-Host ""

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install backend dependencies" -ForegroundColor Red
}
Set-Location ..

Write-Host ""

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
Set-Location tests
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Test dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install test dependencies" -ForegroundColor Red
}
Set-Location ..

Write-Host ""

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install frontend dependencies" -ForegroundColor Red
}
Set-Location ..

Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    
    # Ask about building sandbox
    $buildSandbox = Read-Host "Build Docker sandbox image? (Y/n)"
    if ($buildSandbox -eq "" -or $buildSandbox -eq "Y" -or $buildSandbox -eq "y") {
        Write-Host ""
        Write-Host "Building sandbox image..." -ForegroundColor Yellow
        docker build -f sandbox/Dockerfile.sandbox -t ada-sandbox:latest sandbox/
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Sandbox image built" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to build sandbox image" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "⚠ Docker not found - sandbox will use fallback mode" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Virtual environment is activated and ready!" -ForegroundColor Green
Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run backend:  cd backend; uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host "  2. Run frontend: cd frontend; streamlit run streamlit_app.py" -ForegroundColor Cyan
Write-Host "  3. Run tests:    cd tests; pytest -v" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use Docker Compose:" -ForegroundColor Yellow
Write-Host "  docker-compose up --build" -ForegroundColor Cyan
Write-Host ""
Write-Host "To deactivate venv later:" -ForegroundColor Yellow
Write-Host "  deactivate" -ForegroundColor Cyan
Write-Host ""
Write-Host "To reactivate venv:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
