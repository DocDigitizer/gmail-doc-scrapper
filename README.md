# Gmail Document Scraper

An intelligent, AI-powered agent that automatically extracts and classifies documents (invoices, contracts, receipts, etc.) from your Gmail account. Uses NLP and machine learning to analyze document content, not just keywords.

## Features

- **Intelligent Content Analysis**: Uses spaCy NLP and pattern matching to classify documents based on actual content
- **Multiple Document Types**: Supports invoices, contracts, receipts, fiscal documents, and more
- **Duplicate Detection**: SHA256 hash-based duplicate detection to avoid saving the same document twice
- **OCR Support**: Extracts text from scanned PDFs and images using Tesseract
- **Flexible Organization**: Organizes documents by type and date automatically
- **Detailed Reports**: Generates comprehensive reports of extraction operations
- **Docker Support**: Fully containerized for easy deployment
- **Configurable Rules**: YAML-based classification rules that you can customize

## Table of Contents

- [Installation](#installation)
- [Gmail Setup](#gmail-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Docker Usage](#docker-usage)
- [Document Types](#document-types)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.9+
- Gmail account with IMAP enabled
- Tesseract OCR (optional, for scanned documents)

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://gitlab.com/your-username/gmail-doc-scraper.git
cd gmail-doc-scraper
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy Portuguese model:
```bash
python -m spacy download pt_core_news_lg
```

5. (Optional) Install Tesseract for OCR:
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
   - **macOS**: `brew install tesseract tesseract-lang`
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### Option 2: Docker Installation

```bash
git clone https://gitlab.com/your-username/gmail-doc-scraper.git
cd gmail-doc-scraper
docker-compose build
```

## Gmail Setup

To allow the application to access your Gmail account via IMAP, you need to create an **App Password**. This is more secure than using your regular Gmail password.

### Step-by-Step Guide to Create Gmail App Password

1. **Enable 2-Factor Authentication** (required for App Passwords):
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Under "Signing in to Google", select **2-Step Verification**
   - Follow the prompts to enable 2FA

2. **Generate App Password**:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - You may need to sign in again
   - Select app: Choose **Mail**
   - Select device: Choose **Other (Custom name)** and enter "Gmail Doc Scraper"
   - Click **Generate**
   - Google will display a 16-character password - **copy this immediately**

3. **Save the App Password**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your credentials:
     ```
     GMAIL_EMAIL=your-email@gmail.com
     GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
     ```
   - **Important**: Remove spaces from the app password when pasting

4. **Enable IMAP in Gmail**:
   - Go to [Gmail Settings](https://mail.google.com/mail/u/0/#settings/fwdandpop)
   - Click on **Forwarding and POP/IMAP** tab
   - Enable **IMAP access**
   - Click **Save Changes**

### Security Notes

- App Passwords are safer than your main password
- They can be revoked at any time from [Google Account](https://myaccount.google.com/apppasswords)
- Never commit `.env` file to version control
- The app password only grants access to Gmail, not your entire Google account

## Configuration

### Main Configuration (`config/config.yaml`)

Customize the application behavior:

```yaml
# IMAP settings
imap:
  folders:
    - INBOX
    - "[Gmail]/Sent Mail"

# Document processing
processing:
  enable_ocr: true
  max_file_size_mb: 50
  supported_extensions:
    - .pdf
    - .docx
    - .xlsx

# Classification
classification:
  confidence_threshold: 0.7
  use_ml_model: true

# Output organization
output:
  structure: "type_and_date"  # type_and_date, date_only, or flat
```

### Classification Rules (`config/rules.yaml`)

Define custom document types and classification rules:

```yaml
faturas:
  display_name: "Faturas"
  keywords:
    - fatura
    - invoice
    - NIF
    - total a pagar
  patterns:
    - "Fatura\\s+N[ºo.:]?\\s*\\d+"
    - "NIF\\s*:?\\s*\\d{9}"
  entities:
    - MONEY
    - ORG
    - DATE
  confidence_boost: 0.1
```

## Usage

### Basic Usage

Extract all documents from the last 30 days:
```bash
python main.py --start-date 2024-12-01
```

### Extract Specific Date Range

```bash
python main.py --start-date 2024-01-01 --end-date 2024-12-31
```

### Extract Only Specific Document Types

```bash
python main.py --start-date 2024-01-01 --document-types faturas,contratos
```

### Search in Specific Folder

```bash
python main.py --start-date 2024-01-01 --folder "Work/Invoices"
```

### Dry Run (Test Without Saving)

```bash
python main.py --start-date 2024-12-01 --dry-run
```

### CLI Options

```
Options:
  --start-date YYYY-MM-DD     Start date for email search
  --end-date YYYY-MM-DD       End date for email search
  --document-types TEXT       Comma-separated list of document types
  --folder TEXT               Gmail folder to search (default: INBOX)
  --config-dir PATH           Configuration directory path
  --dry-run                   Run without saving files (for testing)
  --help                      Show this message and exit
```

## Docker Usage

### Build the Image

```bash
docker-compose build
```

### Run with Docker Compose

```bash
# Extract documents from date range
docker-compose run --rm gmail-scraper --start-date 2024-01-01 --end-date 2024-12-31

# Extract only invoices
docker-compose run --rm gmail-scraper --start-date 2024-01-01 --document-types faturas

# Dry run
docker-compose run --rm gmail-scraper --start-date 2024-12-01 --dry-run
```

### Access Output Files

Output files are automatically mounted to your local `./output` directory.

### Run Interactive Shell

```bash
docker-compose run --rm gmail-scraper bash
```

## Document Types

Out of the box, the system recognizes:

- **faturas**: Invoices (PT/EN)
- **contratos**: Contracts
- **recibos**: Receipts
- **documentos_fiscais**: Tax documents

You can add more document types by editing `config/rules.yaml`.

## Output Structure

By default, documents are organized as:

```
output/
├── faturas/
│   ├── 2024-12/
│   │   ├── invoice_001.pdf
│   │   └── invoice_002.pdf
│   └── 2025-01/
│       └── invoice_003.pdf
├── contratos/
│   └── 2024-11/
│       └── contract_xyz.pdf
└── metadata.json
```

The `metadata.json` file contains detailed information about each extracted document.

## Architecture

### Components

- **GmailClient**: IMAP connection and email retrieval
- **EmailParser**: Email parsing and attachment extraction
- **DocumentClassifier**: Intelligent document classification using NLP
- **FileManager**: File organization and duplicate detection
- **ReportGenerator**: Detailed operation reports

### Classification Methods

The classifier uses multiple methods (in order of priority):

1. **Pattern Matching**: Regex patterns for document-specific formats
2. **NLP Analysis**: spaCy named entity recognition
3. **Keyword Matching**: Fallback keyword-based classification

Results are combined with confidence scoring to select the best classification.

## Reports

After each run, you get:

- **Console Report**: Formatted summary in terminal
- **JSON Report**: Detailed report saved to `reports/` directory

Example report output:
```
┌─ Summary ────────────────────────────┐
│ Gmail Document Scraper Report        │
│                                       │
│ Started:  2025-01-15 10:30:00        │
│ Finished: 2025-01-15 10:35:23        │
│ Duration: 0:05:23                     │
└───────────────────────────────────────┘

┌─ Email Processing ───────────────────┐
│ Metric                    │ Count    │
├───────────────────────────┼──────────┤
│ Emails Processed          │ 150      │
│ Emails with Attachments   │ 45       │
│ Total Attachments Found   │ 78       │
└───────────────────────────┴──────────┘

┌─ Document Processing ────────────────┐
│ Metric                    │ Count    │
├───────────────────────────┼──────────┤
│ Documents Classified      │ 65       │
│ Documents Saved           │ 62       │
│ Duplicates Skipped        │ 3        │
│ Classification Failures   │ 13       │
└───────────────────────────┴──────────┘

✓ Successfully extracted 62 documents!
Output directory: ./output
```

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Troubleshooting

### "IMAP authentication failed"
- Make sure you're using an App Password, not your regular Gmail password
- Verify that 2FA is enabled on your Google account
- Check that IMAP is enabled in Gmail settings

### "spaCy model not available"
- Install the Portuguese model: `python -m spacy download pt_core_news_lg`

### "OCR dependencies not installed"
- Install Tesseract OCR system package
- Or disable OCR in `config/config.yaml`: `enable_ocr: false`

### "No documents were extracted"
- Check date range covers emails you expect
- Verify document types are configured in `config/rules.yaml`
- Try `--dry-run` to see what would be classified
- Lower `confidence_threshold` in `config/config.yaml`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Roadmap

- [ ] Support for more email providers (Outlook, etc.)
- [ ] Web UI for browsing extracted documents
- [ ] Machine learning model training from user feedback
- [ ] Support for email forwarding rules
- [ ] Integration with document management systems
- [ ] Multi-language support (currently PT/EN)

## Support

For issues and questions:
- Open an issue on GitLab
- Check existing issues for solutions
- Review documentation in `/docs` directory

---

**Made with ❤️ for automating document management**
