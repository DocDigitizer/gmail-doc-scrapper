# 📧 Gmail Document Scraper

> **Intelligent document extraction and classification from Gmail using AI-powered content analysis**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](DOCKER.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Extract, classify, and organize documents (invoices, contracts, receipts) from your Gmail inbox automatically using machine learning and NLP.

## ✨ Features

- 🤖 **AI-Powered Classification** - Uses spaCy NLP + pattern matching for document classification
- 📄 **PDF Support** - Extracts text from PDF documents with timeout protection
- 🔄 **Smart Deduplication** - SHA256 hashing prevents duplicate file saves
- 📁 **Flexible Organization** - Multiple output structures (by type, by date, flat)
- 🔌 **Resume Capability** - Continue from where you left off with checkpoint system
- 🌍 **Multi-Language** - Supports Portuguese, English, Spanish, and more
- ⚡ **Rate Limit Protection** - Adaptive delays prevent Gmail API throttling
- 🐳 **Docker Ready** - Complete Docker and Docker Compose support
- 🔒 **Secure** - App passwords only, credentials never stored in code

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/gmail-doc-scrapper.git
cd gmail-doc-scrapper

# Create .env file
cp .env.example .env
# Edit .env with your Gmail credentials

# Run with Docker Compose
docker-compose run --rm gmail-scraper --interactive
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation.

### Option 2: Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/gmail-doc-scrapper.git
cd gmail-doc-scrapper

# Automated setup (Unix/Linux/macOS)
./setup.sh

# Or Windows PowerShell
.\setup.ps1
```

### First Run

```bash
# Interactive mode
python main.py --interactive
```

**Example:**
```
Gmail email: your-email@gmail.com
Gmail App Password: xxxx-xxxx-xxxx-xxxx
Start date: 2024-01-01
End date: 2024-12-31
Folder: INBOX
```

## 📖 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions
- **[Docker Guide](DOCKER.md)** - Docker & Docker Compose setup
- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Resume Functionality](RESUME_GUIDE.md)** - Continue interrupted runs
- **[Testing Guide](TEST_GUIDE.md)** - Running tests
- **[Contributing](CONTRIBUTING.md)** - How to contribute

## 🎯 Usage Examples

```bash
# Interactive mode
python main.py --interactive

# Resume from checkpoint
python main.py --resume

# Specific date range
python main.py --start-date 2024-01-01 --end-date 2024-12-31

# Extract only invoices
python main.py --document-types invoices

# Docker interactive
docker-compose run --rm gmail-scraper --interactive
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### Classification Rules (config/rules.yaml)

```yaml
invoices:
  display_name: "Invoices"
  keywords:
    - invoice
    - bill
  patterns:
    - "Invoice\\s+#?\\d+"
```

## 🔐 Gmail Setup

1. Enable IMAP in Gmail Settings
2. Enable 2-Factor Authentication
3. Generate App Password at [Google Account Security](https://myaccount.google.com/security)
4. Add to `.env` file

## 📊 Output Structure

```
output/
├── invoices/
│   ├── 2024-01/
│   │   ├── invoice_001.pdf
│   │   └── invoice_002.pdf
│   └── 2024-02/
│       └── invoice_003.pdf
└── metadata.json

reports/
├── report_20240101_120000.json
├── .checkpoint.json
└── .last_run.json
```

## ⚠️ Limitations & Known Issues

### Current Classification Limitations

This project uses **rule-based classification** (pattern matching + NLP) with some limitations:

- **Accuracy:** ~85-90% for well-formatted documents
- **Language Support:** Best for English and Portuguese
- **OCR:** Disabled by default (requires Tesseract installation)
- **Complex Documents:** May misclassify unusual formats
- **Custom Types:** Requires manual rule configuration

### 🚀 Need Better Classification?

**Enhanced LLM-Powered Solution Available!**

I offer a **premium add-on** with advanced capabilities:

✅ **LLM-Based Classification**
- **95%+ accuracy** using GPT-4/Claude
- Understands context, not just patterns
- Handles complex and multi-page documents
- Works with scanned/OCR documents

✅ **Advanced Document Analysis**
- Extract structured metadata (dates, amounts, parties, line items)
- Multi-language support (30+ languages)
- Custom document types without manual configuration
- Confidence scoring with explanations

✅ **CSV/Excel Export**
- Export extracted metadata to CSV/Excel format
- Customizable fields and column mapping
- Batch export capabilities
- Direct integration with accounting software (QuickBooks, Xero, SAP)

✅ **Production Support**
- Priority email support with SLA
- Custom integrations and API endpoints
- Training for your specific document types
- Dedicated support channel

**Interested?** Contact me for pricing, demo, and trial access:

📧 **Email:** [joao.fernandes@docdigitizer.com](mailto:joao.fernandes@docdigitizer.com)

**Subject:** "Gmail Scraper - LLM Add-on Interest"

**Include in your email:**
- Current document volume (emails/month)
- Document types you need to process
- Required languages
- Integration needs (if any)

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Quick test (10 emails)
python test_quick.py

# Installation verification
python test_installation.py
```

## 🛠️ Troubleshooting

**"Authentication failed"**
- Use App Password (not regular password)
- Verify 2FA is enabled
- Check IMAP is enabled

**"Too many consecutive fetch failures"**
- Gmail rate limiting detected
- Wait 15-30 minutes
- Run `python main.py --resume`

**"spaCy model not found"**
```bash
python -m spacy download pt_core_news_lg
```

See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting.

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) - NLP library
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF extraction
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Click](https://click.palletsprojects.com/) - CLI framework

## 📞 Support

### Community Support (Free)

- **Issues:** [GitHub Issues](https://github.com/yourusername/gmail-doc-scrapper/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/gmail-doc-scrapper/discussions)

### Commercial Support & Add-ons

📧 **Email:** [joao.fernandes@docdigitizer.com](mailto:joao.fernandes@docdigitizer.com)

**Services:**
- LLM-powered classification add-on (95%+ accuracy)
- Advanced metadata extraction and CSV export
- Custom integrations and API development
- Training and consultation
- Production deployment support

---

**Made with ❤️ for document automation**

**⭐ Star this repository if you find it useful!**

**💬 Questions? Contact:** [joao.fernandes@docdigitizer.com](mailto:joao.fernandes@docdigitizer.com)
