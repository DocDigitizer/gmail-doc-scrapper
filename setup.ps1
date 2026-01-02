# Gmail Document Scraper - Setup Script
# Automated installation for Windows (PowerShell)

Write-Host "📧 Gmail Document Scraper - Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check pip
Write-Host "Checking pip..." -ForegroundColor Yellow
try {
    python -m pip --version | Out-Null
    Write-Host "✓ pip is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: pip not found" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  venv already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Install spaCy model
Write-Host ""
Write-Host "Installing spaCy Portuguese language model..." -ForegroundColor Yellow
python -m spacy download pt_core_news_lg
Write-Host "✓ spaCy model installed" -ForegroundColor Green

# Create .env if doesn't exist
if (!(Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env file and add your Gmail credentials:" -ForegroundColor Yellow
    Write-Host "   GMAIL_EMAIL=your-email@gmail.com" -ForegroundColor White
    Write-Host "   GMAIL_APP_PASSWORD=your-app-password" -ForegroundColor White
}

# Create output directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path output | Out-Null
New-Item -ItemType Directory -Force -Path reports | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green

# Run installation test
Write-Host ""
Write-Host "Running installation test..." -ForegroundColor Yellow
python test_installation.py

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your credentials" -ForegroundColor White
Write-Host "2. Run: python main.py --interactive" -ForegroundColor White
Write-Host ""
Write-Host "For help: python main.py --help" -ForegroundColor White
Write-Host "==============================================" -ForegroundColor Cyan
