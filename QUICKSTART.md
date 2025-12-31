# Quick Start Guide

Get up and running with Gmail Document Scraper in 5 minutes!

## Prerequisites

- Python 3.9+ or Docker
- Gmail account with 2FA enabled
- 5 minutes of your time

## Quick Setup (Docker - Recommended)

### 1. Clone and Setup

```bash
git clone https://gitlab.com/your-username/gmail-doc-scraper.git
cd gmail-doc-scraper
cp .env.example .env
```

### 2. Configure Gmail Access

Edit `.env` file:
```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password-here
```

**Get App Password**: [Google App Passwords](https://myaccount.google.com/apppasswords)
- Enable 2FA first if not already enabled
- Generate password for "Mail" + "Other (Gmail Doc Scraper)"
- Copy the 16-character password (remove spaces)

### 3. Build and Run

```bash
# Build Docker image
docker-compose build

# Extract documents from last 30 days
docker-compose run --rm gmail-scraper --start-date 2024-12-01

# Extract only invoices
docker-compose run --rm gmail-scraper --start-date 2024-01-01 --document-types faturas
```

### 4. Check Results

```bash
ls output/
```

Documents will be organized in `output/` by type and date!

---

## Quick Setup (Python)

### 1. Clone and Setup

```bash
git clone https://gitlab.com/your-username/gmail-doc-scraper.git
cd gmail-doc-scraper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your Gmail credentials
```

### 4. Run

```bash
python main.py --start-date 2024-12-01
```

---

## Common Use Cases

### Extract all documents from 2024
```bash
python main.py --start-date 2024-01-01 --end-date 2024-12-31
```

### Extract only invoices and contracts
```bash
python main.py --start-date 2024-01-01 --document-types faturas,contratos
```

### Test without saving (dry run)
```bash
python main.py --start-date 2024-12-01 --dry-run
```

### Search in specific folder
```bash
python main.py --start-date 2024-01-01 --folder "Work/Invoices"
```

---

## Makefile Commands

If you have `make` installed:

```bash
make install       # Install all dependencies
make test          # Run tests
make format        # Format code
make docker-build  # Build Docker image
make docker-run ARGS="--start-date 2024-01-01"  # Run with Docker
```

---

## Troubleshooting

### "IMAP authentication failed"
- ✓ Use App Password, not regular password
- ✓ Enable 2FA in Google Account
- ✓ Enable IMAP in Gmail settings
- ✓ Remove spaces from app password in .env

### "spaCy model not available"
```bash
python -m spacy download pt_core_news_lg
```

### "No documents found"
- Try broader date range
- Lower confidence threshold in `config/config.yaml`
- Use `--dry-run` to see what would be classified

---

## Next Steps

1. **Customize classification rules**: Edit `config/rules.yaml`
2. **Add new document types**: See CONTRIBUTING.md
3. **Adjust confidence threshold**: Edit `config/config.yaml`
4. **Review output structure**: Check `config/config.yaml` → `output.structure`

---

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Report issues: [GitLab Issues](https://gitlab.com/your-username/gmail-doc-scraper/-/issues)
- 💡 Feature requests: [GitLab Issues](https://gitlab.com/your-username/gmail-doc-scraper/-/issues)

**Happy document extracting! 🚀**
