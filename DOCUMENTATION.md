# 📚 Documentation Index

Complete documentation for Gmail Document Scraper.

## Getting Started

1. **[README](README.md)** - Project overview and quick start
2. **[Installation Guide](INSTALLATION.md)** - Detailed installation instructions
3. **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes

## User Guides

### Core Features
- **[Resume Functionality](RESUME_GUIDE.md)** - Continue interrupted runs
- **[Testing Guide](TEST_GUIDE.md)** - Running tests
- **[Folder Search](FOLDER_SEARCH_EXAMPLES.md)** - Search multiple Gmail folders
- **[Automatic Folder Search](AUTOMATIC_FOLDER_SEARCH.md)** - Auto-discover folders

### Configuration
- **[Configuration Files](config/README.md)** - config.yaml and rules.yaml
- **Environment Variables** - See [.env.example](.env.example)

## Technical Documentation

### Architecture & Design
- **[Classification Algorithm](INVOICE_CLASSIFICATION_ALGORITHM.md)** - Document classification explained
- **[Connection Keepalive](CONNECTION_KEEPALIVE.md)** - IMAP connection management
- **[For Claude Code](CLAUDE.md)** - AI assistant documentation

### Code Structure
```
gmail-doc-scrapper/
├── main.py                    # CLI entry point
├── src/
│   ├── gmail_client.py        # IMAP connection
│   ├── email_parser.py        # Email/attachment parsing
│   ├── document_classifier.py # AI classification
│   ├── file_manager.py        # File operations
│   └── report_generator.py   # Report generation
├── config/
│   ├── config.yaml           # Main configuration
│   └── rules.yaml            # Classification rules
└── tests/                    # Unit tests
```

## Developer Documentation

### Contributing
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/gmail-doc-scrapper.git
cd gmail-doc-scrapper

# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov=src
```

### Code Quality
- **Black** - Code formatting (line length: 100)
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing

## API Reference

### GmailClient
```python
from src.gmail_client import GmailClient

client = GmailClient(email, password)
client.connect()
client.select_folder('INBOX')
email_ids = client.search_emails(start_date, end_date)
```

### DocumentClassifier
```python
from src.document_classifier import DocumentClassifier

classifier = DocumentClassifier(config, rules)
result = classifier.classify_document(file_path, text_content)
# Returns: ClassificationResult(document_type, confidence, display_name)
```

### FileManager
```python
from src.file_manager import FileManager

manager = FileManager(config)
output_path = manager.save_file(
    content=pdf_bytes,
    document_type='invoices',
    original_filename='invoice.pdf',
    email_metadata=metadata,
    classification_confidence=0.85
)
```

## Configuration Reference

### config.yaml

```yaml
processing:
  max_file_size_mb: 50            # Maximum file size to process
  supported_extensions:           # File types to extract
    - .pdf
  enable_ocr: false              # OCR for scanned documents

classification:
  confidence_threshold: 0.5       # Minimum confidence to classify
  min_text_length: 30            # Minimum text length required
  use_ml_model: false            # Use ML model (if trained)

output:
  structure: type_and_date       # Output organization
  base_dir: ./output             # Output directory
  metadata_file: metadata.json   # Metadata filename
```

### rules.yaml

```yaml
document_type_id:
  display_name: "Document Type"  # Human-readable name
  keywords:                      # Keywords to match
    - keyword1
    - keyword2
  entities:                      # spaCy entities to look for
    - MONEY
    - ORG
  patterns:                      # Regex patterns
    - "Pattern\\s+\\d+"
  confidence_boost: 0.15         # Confidence boost if matched
```

## Command Reference

### Basic Commands

```bash
# Interactive mode (recommended for first use)
python main.py --interactive

# Resume from checkpoint
python main.py --resume

# Specific date range
python main.py --start-date 2024-01-01 --end-date 2024-12-31

# Specific document types
python main.py --document-types invoices,contracts

# Specific folder
python main.py --folder INBOX

# Dry run (no file saving)
python main.py --dry-run
```

### Testing Commands

```bash
# Quick test (10 emails)
python test_quick.py

# Installation test
python test_installation.py

# Full test suite
pytest tests/ -v

# Coverage report
pytest tests/ --cov=src --cov-report=html
```

### Utility Commands

```bash
# Format code
black main.py src/ tests/

# Sort imports
isort main.py src/ tests/

# Lint code
flake8 main.py src/ tests/

# Type check
mypy main.py src/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Troubleshooting

### Common Issues

**Problem:** "Authentication failed"
- **Solution:** Check 2FA is enabled, use App Password, verify IMAP enabled

**Problem:** "Too many consecutive fetch failures"
- **Solution:** Gmail rate limiting. Wait 15-30 min, run `--resume`

**Problem:** "spaCy model not found"
- **Solution:** `python -m spacy download pt_core_news_lg`

**Problem:** "Connection timeout"
- **Solution:** Script auto-reconnects. Progress saved via checkpoint.

See [Installation Guide](INSTALLATION.md) for detailed troubleshooting.

## FAQ

**Q: How do I process only invoices?**
```bash
python main.py --document-types invoices
```

**Q: Can I resume if the script stops?**
```bash
python main.py --resume
```

**Q: How do I search all folders?**
```bash
python main.py --folder ALL
```

**Q: Where are extracted documents saved?**
- Default: `./output/document_type/YYYY-MM/`
- Configurable in `config/config.yaml`

**Q: How do I add custom document types?**
- Edit `config/rules.yaml`
- Add new document type with keywords, patterns, entities

**Q: Is OCR supported?**
- Yes, but requires Tesseract installation
- Set `enable_ocr: true` in `config/config.yaml`

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/gmail-doc-scrapper/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/gmail-doc-scrapper/discussions)
- **Email:** support@example.com

## Additional Resources

- [spaCy Documentation](https://spacy.io/usage)
- [Gmail IMAP Documentation](https://support.google.com/mail/answer/7126229)
- [Python Email Library](https://docs.python.org/3/library/email.html)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)

---

**Last Updated:** 2026-01-02
