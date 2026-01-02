# 📦 Installation Guide

Complete installation instructions for Gmail Document Scraper.

## Prerequisites

### System Requirements

- **Operating System:** Windows, macOS, or Linux
- **Python:** Version 3.8 or higher
- **RAM:** Minimum 2GB (4GB+ recommended for large mailboxes)
- **Disk Space:** ~500MB for dependencies + space for extracted documents

### Gmail Requirements

- Gmail account with IMAP access
- 2-Factor Authentication enabled
- App Password generated

## Step-by-Step Installation

### 1. Install Python

#### Windows
Download from [python.org](https://www.python.org/downloads/) and run installer.
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

Verify installation:
```powershell
python --version
pip --version
```

#### macOS
```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

### 2. Clone Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/gmail-doc-scrapper.git

# Or using SSH
git clone git@github.com:yourusername/gmail-doc-scrapper.git

cd gmail-doc-scrapper
```

### 3. Create Virtual Environment

**Why virtual environment?**
- Isolates project dependencies
- Prevents conflicts with system packages
- Easy to delete and recreate

#### All Platforms
```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Your prompt should now show (venv)
```

### 4. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This installs:
# - rich (terminal UI)
# - click (CLI framework)
# - spacy (NLP)
# - pdfplumber (PDF extraction)
# - PyPDF2 (PDF fallback)
# - python-dotenv (environment variables)
```

### 5. Install spaCy Language Model

```bash
# Portuguese model (recommended)
python -m spacy download pt_core_news_lg

# Or English model
python -m spacy download en_core_web_lg

# Verify installation
python -c "import spacy; nlp = spacy.load('pt_core_news_lg'); print('✓ spaCy model loaded')"
```

### 6. Configure Credentials

#### Create .env file
```bash
cp .env.example .env
```

#### Edit .env
```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

**Get App Password:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already)
3. Search for "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Copy the 16-character password
6. Paste into `.env` file

### 7. Verify Installation

```bash
# Run installation test
python test_installation.py

# Expected output:
# ✓ Python version: 3.x.x
# ✓ Dependencies installed
# ✓ spaCy model loaded
# ✓ Configuration files found
# ✓ All checks passed!
```

## Optional: Enable IMAP in Gmail

1. Open Gmail in browser
2. Click ⚙️ Settings → "See all settings"
3. Go to "Forwarding and POP/IMAP" tab
4. Enable "IMAP Access"
5. Click "Save Changes"

## Troubleshooting

### "Python not found"
- Ensure Python is in PATH
- Try `python3` instead of `python`
- Restart terminal/PowerShell

### "pip not found"
```bash
# Install pip manually
python -m ensurepip --upgrade
```

### "spaCy model not found"
```bash
# Check installed models
python -m spacy info

# Reinstall model
python -m spacy download pt_core_news_lg --force
```

### "No module named 'X'"
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### "Authentication failed"
- Verify 2FA is enabled
- Regenerate App Password
- Check for typos in `.env`
- Remove spaces from App Password

### "IMAP not enabled"
- Follow "Enable IMAP in Gmail" section above
- Wait 5 minutes for changes to propagate

## Platform-Specific Notes

### Windows

**PowerShell Execution Policy:**
```powershell
# If venv activation fails:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Long Path Support:**
```powershell
# Enable if you encounter path length errors
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### macOS

**Xcode Command Line Tools:**
```bash
# Required for some Python packages
xcode-select --install
```

### Linux

**Additional Dependencies:**
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc python3-devel
```

## Development Installation

For contributors:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

## Docker Installation

Alternative containerized installation:

```bash
# Build image
docker-compose build

# Run
docker-compose up
```

See [Docker documentation](docs/DOCKER.md) for details.

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Update spaCy model
python -m spacy download pt_core_news_lg --force
```

## Uninstalling

```bash
# Deactivate venv
deactivate

# Remove directory
cd ..
rm -rf gmail-doc-scrapper

# Or on Windows:
rmdir /s gmail-doc-scrapper
```

## Next Steps

After installation:

1. ✅ Run `python test_installation.py` to verify
2. ✅ Read [QUICKSTART.md](QUICKSTART.md) for first use
3. ✅ Check [RESUME_GUIDE.md](RESUME_GUIDE.md) for resume functionality
4. ✅ Customize `config/rules.yaml` for your needs

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/gmail-doc-scrapper/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/gmail-doc-scrapper/discussions)
