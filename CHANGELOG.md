# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-15

### Added
- Initial release of Gmail Document Scraper
- IMAP-based Gmail connection with App Password support
- Intelligent document classification using NLP and pattern matching
- Support for multiple document types (invoices, contracts, receipts, fiscal documents)
- Content-based classification using spaCy Portuguese NLP model
- Pattern matching with regex for document-specific formats
- Keyword-based classification as fallback method
- SHA256 hash-based duplicate detection
- OCR support for scanned documents using Tesseract
- Flexible document organization (by type and date, date only, or flat structure)
- Comprehensive reporting system (console and JSON formats)
- Docker support with docker-compose configuration
- CLI interface with multiple options and filters
- Configurable classification rules via YAML
- Extensive documentation and setup guides
- Unit tests with pytest
- GitLab CI/CD pipeline configuration
- MIT License

### Features
- Extract documents from Gmail within date ranges
- Filter by specific document types
- Process multiple Gmail folders
- Dry-run mode for testing
- Detailed metadata tracking for all extracted documents
- Progress bars and rich console output
- Automatic folder organization
- Configurable confidence thresholds
- Support for PDF, DOCX, XLSX, and image formats
- Multi-language support (Portuguese and English)

### Documentation
- Comprehensive README with setup instructions
- Detailed Gmail App Password setup guide
- Docker usage examples
- Configuration documentation
- Contributing guidelines
- Troubleshooting section
- API documentation for all modules

## [Unreleased]

### Planned Features
- Support for more email providers (Outlook, Office 365)
- Web UI for browsing extracted documents
- Machine learning model training from user feedback
- Email forwarding rules integration
- Document management system integration
- Additional language support
- Advanced search capabilities
- Document preview in CLI
- Batch processing improvements
- Rate limiting and quota management

---

For more information, see the [README](README.md).
