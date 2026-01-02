#!/bin/bash
# Gmail Document Scraper - Setup Script
# Automated installation for Unix/Linux/macOS

set -e  # Exit on error

echo "📧 Gmail Document Scraper - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check pip
echo "Checking pip..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "✓ pip is available"
else
    echo "❌ Error: pip not found"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  venv already exists, skipping..."
else
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Install spaCy model
echo ""
echo "Installing spaCy Portuguese language model..."
python -m spacy download pt_core_news_lg
echo "✓ spaCy model installed"

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Gmail credentials:"
    echo "   GMAIL_EMAIL=your-email@gmail.com"
    echo "   GMAIL_APP_PASSWORD=your-app-password"
fi

# Create output directories
echo ""
echo "Creating directories..."
mkdir -p output reports
echo "✓ Directories created"

# Run installation test
echo ""
echo "Running installation test..."
python test_installation.py

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python main.py --interactive"
echo ""
echo "For help: python main.py --help"
echo "=============================================="
