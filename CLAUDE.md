# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gmail Document Scraper is an AI-powered Python application that extracts and classifies documents (invoices, contracts, receipts, tax documents) from Gmail accounts. It uses NLP (spaCy), pattern matching, and keyword analysis to intelligently classify document types with confidence scoring.

**Requirements:** Python 3.9+

## Development Commands

### Setup and Installation
```bash
# Automated setup (recommended)
./setup.sh              # Unix/Linux/macOS
.\setup.ps1             # Windows PowerShell

# Manual setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy Portuguese model (required)
python -m spacy download pt_core_news_lg

# Install dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks (recommended)
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_document_classifier.py -v

# Run tests without coverage
pytest tests/ -v

# Run tests excluding slow ones
pytest -m "not slow" -v

# Quick integration test (10 emails)
python test_quick.py

# Installation verification
python test_installation.py
```

### Code Quality
```bash
# Format code with black (line length: 100)
black src/ tests/ main.py

# Check formatting without modifying
black --check src/ tests/ main.py

# Run linting
flake8 src/ tests/ --max-line-length=100

# Sort imports
isort src/ tests/ --profile black

# Run pre-commit hooks manually
pre-commit run --all-files

# Type checking
mypy src/ --ignore-missing-imports
```

### Running the Application
```bash
# Interactive mode (recommended for testing)
python main.py --interactive

# Resume from last checkpoint
python main.py --resume

# Basic usage
python main.py --start-date 2024-01-01 --end-date 2024-12-31

# Dry run (test without saving files)
python main.py --start-date 2024-01-01 --dry-run

# Extract specific document types
python main.py --start-date 2024-01-01 --document-types invoices,contracts

# Search specific folder
python main.py --start-date 2024-01-01 --folder "INBOX"

# Docker
docker-compose build
docker-compose run --rm gmail-scraper --interactive
docker-compose run --rm gmail-scraper --resume
```

### Makefile Shortcuts
```bash
make install      # Install dependencies and setup
make dev-setup    # Install with dev dependencies
make test         # Run tests with coverage
make lint         # Run code linting
make format       # Format code with black
make check        # Run lint + test
make clean        # Clean temporary files
make docker-build # Build Docker image
make docker-run   # Run with Docker (set ARGS="--interactive")
make run          # Run application (set ARGS="--start-date 2024-01-01")
```

## Architecture

### Core Components

The application follows a modular pipeline architecture:

1. **GmailClient** (`src/gmail_client.py`) - IMAP connection management
   - Connects to Gmail via IMAP SSL (port 993)
   - Implements connection keepalive (NOOP every 5 minutes) to prevent 30-minute timeout
   - Auto-reconnection with folder state restoration
   - Searches emails by date range and fetches individual messages

2. **EmailParser** (`src/email_parser.py`) - Email processing
   - Extracts attachments from email messages
   - Decodes email headers (subject, from, date)
   - Filters attachments by supported extensions (.pdf, .docx, .xlsx, .png, .jpg)

3. **DocumentClassifier** (`src/document_classifier.py`) - Intelligent classification
   - Uses 3-tier hybrid approach (pattern matching, NLP entities, keywords)
   - Extracts text from PDFs (PyPDF2, pdfplumber) and DOCX files
   - spaCy NLP for named entity recognition (MONEY, ORG, DATE, etc.)
   - Confidence scoring with configurable threshold (default: 0.7)
   - Returns best classification result across all methods

4. **FileManager** (`src/file_manager.py`) - File organization
   - SHA256 hash-based duplicate detection
   - Organizes files by document type and date (configurable)
   - Maintains metadata.json with file records
   - Handles filename collisions

5. **ReportGenerator** (`src/report_generator.py`) - Reporting
   - Console reports with Rich formatting
   - JSON reports saved to reports/ directory
   - Statistics: emails processed, documents classified, duplicates skipped

6. **ConfigLoader** (`src/config_loader.py`) - Configuration management
   - Loads config.yaml and rules.yaml
   - Validates configuration schema
   - Provides centralized config access

### Data Flow

```
Gmail IMAP → EmailParser → DocumentClassifier → FileManager → ReportGenerator
     ↓            ↓               ↓                   ↓              ↓
  Fetch      Extract         Classify            Save           Report
  emails     attachments     document type       with hash      statistics
```

### Classification Algorithm

Document classification uses a 3-tier hybrid system (see INVOICE_CLASSIFICATION_ALGORITHM.md for details):

1. **Pattern Matching** (highest priority) - Regex patterns for document-specific formats
   - Example: "Fatura\\s+N[ºo.:]?\\s*\\d+" matches "Fatura Nº 2024/123"
   - Confidence: `(matches/total) × 0.8 + 0.2 + boost`

2. **NLP Entity Recognition** (spaCy) - Extracts named entities
   - Example: MONEY (€150.00), ORG (company names), DATE (2024-12-31)
   - Confidence: `(entities_found/required) × 0.7 + 0.2 + boost`

3. **Keyword Matching** (fallback) - Simple keyword counting
   - Example: "invoice", "fatura", "NIF", "total"
   - Confidence: `(keywords_found/total) × 0.6 + 0.15` (max 0.85)

Best result (highest confidence) wins. Must exceed threshold (default 0.7) to classify.

### Connection Keepalive System

Gmail IMAP connections timeout after ~30 minutes of inactivity. The keepalive system prevents this:

- **Automatic NOOP**: Sends IMAP NOOP command every 5 minutes (300s)
- **Connection Check**: Verifies connection health before each fetch
- **Auto-Reconnect**: Detects dropped connections and reconnects automatically
- **State Restoration**: Reselects the same folder after reconnection

See CONNECTION_KEEPALIVE.md for implementation details.

### Configuration Files

**config/config.yaml** - Main configuration
- IMAP settings (server, port, folders)
- Processing options (OCR, file size limits, supported extensions)
- Classification thresholds and ML settings
- Output organization structure
- Duplicate detection method (hash/filename/both)

**config/rules.yaml** - Document classification rules
- Document types: invoices, contracts, receipts, tax_documents
- Each type has: keywords, patterns (regex), entities (NLP), confidence_boost
- Easily extensible by adding new document types

**.env** - Credentials (not in repo)
```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

## Important Implementation Details

### Gmail Authentication
- Requires Gmail App Password (not regular password)
- 2FA must be enabled on Google account
- IMAP must be enabled in Gmail settings
- Generate at: https://myaccount.google.com/apppasswords

### Text Extraction Priority
For PDFs, the classifier tries multiple methods in order:
1. pdfplumber (best for complex layouts)
2. PyPDF2 (fallback for simple PDFs)
3. OCR with Tesseract (for scanned documents, if enabled)

### Folder Search Behavior
- Default: Searches all Gmail folders automatically (folder="ALL")
- main.py line 90: `folder = "ALL"` sets auto-search mode
- GmailClient.list_folders() returns all available folders
- Processes folders sequentially, combining results

### Duplicate Detection
- SHA256 hash calculated from file content (not filename)
- Duplicate check before saving (file_manager.py)
- Existing files tracked in metadata.json
- Action: skip (default), rename, or overwrite

### Error Handling
- NoneType errors fixed with robust null checking (see ERROR_FIX_NOTES.md)
- Connection failures trigger auto-reconnect (max 1 retry)
- Classification failures logged but don't stop processing
- OCR failures fall back to pattern/keyword matching

## Testing

### Test Structure
```
tests/
├── test_config_loader.py       # Config validation
├── test_document_classifier.py # Classification logic
└── test_file_manager.py        # File operations
```

### Running Specific Tests
```bash
# Test classifier only
pytest tests/test_document_classifier.py -v

# Test with specific markers
pytest -m "not slow" -v
pytest -m integration -v

# Test installation script
python test_installation.py

# Test with specific function
pytest tests/test_document_classifier.py::test_classify_invoice -v
```

### Coverage Requirements
- Aim for >80% coverage on src/ modules
- View HTML report: `htmlcov/index.html` after running tests
- Coverage config in pyproject.toml (excludes tests, abstracts, TYPE_CHECKING blocks)

## CI/CD

GitLab CI pipeline (.gitlab-ci.yml):
- **Runs on**: merge_requests, main, master, develop
- **Stages**: test, code-quality, build, deploy (pages)
- **Python version**: 3.11 (configurable via PYTHON_VERSION variable)
- **Test stage**: Installs dependencies, downloads spaCy model, runs pytest with coverage
- **Code quality stage**: Runs black --check and flake8 (allow_failure: true)
- **Build stage**: Builds and pushes Docker image to GitLab registry
- **Deploy stage**: Builds mkdocs documentation to GitLab Pages (main/master only)
- **Artifacts**: Coverage reports (1 week retention), htmlcov/

## Common Development Tasks

### Adding a New Document Type
1. Edit `config/rules.yaml`, add new entry with keywords, patterns, entities
2. Set confidence_boost if needed (0.1 = +10%)
3. Test with sample documents using `--dry-run`
4. Adjust patterns/keywords based on results

### Adjusting Classification Sensitivity
- **Stricter** (fewer false positives): Increase `confidence_threshold` in config.yaml to 0.8-0.85
- **Lenient** (catch more): Decrease to 0.6, add more keywords to rules.yaml
- **Per-type tuning**: Adjust confidence_boost in rules.yaml

### Debugging Classification Issues
```bash
# Dry run shows classification results without saving
python main.py --start-date 2024-01-01 --dry-run

# Check what was classified
cat reports/report_*.json | grep -A5 "document_type"

# Enable detailed logging in config.yaml
reporting:
  detailed_log: true
  log_level: DEBUG
```

### Performance Tuning
Adjust in config.yaml:
- `batch_size`: Number of emails per batch (default: 50)
- `max_workers`: Parallel threads (default: 4)
- Keepalive interval: Edit gmail_client.py line 96 (default: 300s)

## Output Structure

Default organization (`structure: "type_and_date"`):
```
output/
├── invoices/
│   ├── 2024-12/
│   │   └── invoice_001.pdf
│   └── 2025-01/
│       └── invoice_002.pdf
├── contracts/
│   └── 2024-11/
│       └── contract_xyz.pdf
├── metadata.json          # All file records
└── .../
```

Alternatives:
- `date_only`: Organize by date only
- `flat`: All files in output/ root

## Dependencies

Critical runtime dependencies (requirements.txt):
- **spacy** + pt_core_news_lg: Portuguese NLP model (required for entity recognition)
- **pdfplumber**: PDF text extraction (primary method)
- **PyPDF2**: Fallback PDF parser
- **python-docx**: DOCX file parsing
- **pytesseract**: OCR for scanned documents (optional, requires system Tesseract)
- **rich**: Terminal formatting and progress bars
- **click**: CLI argument parsing
- **pyyaml**: Configuration loading
- **python-dotenv**: Environment variable management

Development dependencies (requirements-dev.txt):
- **pytest**, **pytest-cov**, **pytest-mock**, **pytest-asyncio**: Testing framework
- **black**: Code formatter (line-length: 100)
- **flake8**: Linter (max-line-length: 100, ignore: E203, W503)
- **isort**: Import sorting (profile: black)
- **mypy**: Type checking
- **pre-commit**: Git hooks for code quality
- **mkdocs**, **mkdocs-material**: Documentation generation
- **ipython**, **ipdb**: Development/debugging tools

## Pre-commit Hooks

The project uses pre-commit hooks (.pre-commit-config.yaml) for automated code quality:
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures newline at EOF
- **check-yaml**: Validates YAML syntax
- **check-added-large-files**: Prevents commits >1MB
- **check-merge-conflict**: Detects merge conflict markers
- **debug-statements**: Catches debug statements
- **black**: Auto-formats code (line-length: 100)
- **isort**: Sorts imports (profile: black)
- **flake8**: Linting (max-line-length: 100)
- **mypy**: Type checking (ignore-missing-imports)

Install hooks: `pre-commit install`
Run manually: `pre-commit run --all-files`

## Project Structure

```
gmail-doc-scrapper/
├── src/                        # Core application modules
│   ├── gmail_client.py         # IMAP connection & keepalive
│   ├── email_parser.py         # Email/attachment extraction
│   ├── document_classifier.py  # 3-tier classification system
│   ├── file_manager.py         # Deduplication & file organization
│   ├── report_generator.py     # Console & JSON reports
│   └── config_loader.py        # Config validation & loading
├── tests/                      # Unit tests (pytest)
├── config/                     # YAML configuration files
│   ├── config.yaml             # Main settings
│   └── rules.yaml              # Document classification rules
├── main.py                     # CLI entry point
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Build config & tool settings
├── Makefile                    # Common command shortcuts
├── setup.sh / setup.ps1        # Automated setup scripts
├── .pre-commit-config.yaml     # Pre-commit hooks config
├── .gitlab-ci.yml              # GitLab CI/CD pipeline
├── Dockerfile                  # Docker image definition
└── docker-compose.yml          # Docker Compose config
```

## Build Configuration (pyproject.toml)

- **Package name**: gmail-doc-scraper v1.0.0
- **Python requirement**: >=3.9
- **Build system**: setuptools + wheel
- **CLI entry point**: `gmail-scraper` command (via project.scripts)
- **Black config**: line-length=100, target py39/py310/py311
- **Pytest markers**: `slow`, `integration`
- **Coverage**: source=src, omit=tests, HTML + term reports
- **Flake8**: max-line-length=100, ignore E203 (whitespace before ':') and W503 (line break before binary operator)

## Notes for Future Development

- spaCy model is optional but highly recommended (better classification accuracy)
- OCR requires Tesseract system package (not just Python package)
- Connection keepalive critical for processing >100 emails (prevents timeout)
- Duplicate detection relies on file content hash, not filename
- Classification confidence scores are transparent and logged for debugging
- All configuration is YAML-based (no hardcoded values in code)
- Reports are saved to reports/ directory with timestamp
- Resume functionality stores state in reports/.last_run.json and reports/.checkpoint.json
- Folder search default is "ALL" (main.py line 90) - searches all Gmail folders automatically
- Windows compatibility: Uses Path objects, has setup.ps1, handles newlines correctly
