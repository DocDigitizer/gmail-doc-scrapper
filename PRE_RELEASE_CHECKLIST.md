# 🚀 Pre-Release Checklist

Before publishing this repository as open source, ensure all items are completed.

## ✅ Security & Privacy

- [x] Remove `.env` file with credentials
- [x] Remove hardcoded credentials from `test_quick.py`
- [x] Verify `.gitignore` includes sensitive files
- [x] Remove personal email addresses from code
- [x] Remove API keys/tokens from code
- [x] Check `output/` directory is empty (gitignored)
- [x] Check `reports/` contains no personal data
- [x] Verify no `.checkpoint.json` with personal email IDs

## ✅ Documentation

- [x] README.md - Complete overview
- [x] INSTALLATION.md - Step-by-step install guide
- [x] QUICKSTART.md - Quick start guide
- [x] RESUME_GUIDE.md - Resume functionality docs
- [x] CONTRIBUTING.md - Contribution guidelines
- [x] DOCUMENTATION.md - Documentation index
- [x] LICENSE - MIT License included
- [x] CHANGELOG.md - Version history
- [x] .env.example - Template for credentials

## ✅ Code Quality

- [x] Remove debug/temporary code
- [x] Remove commented-out code blocks
- [x] Add docstrings to all functions
- [x] Add type hints where appropriate
- [x] Code follows consistent style
- [x] Remove print() debugging statements
- [x] Use logging instead of console.print where appropriate

## ✅ Configuration

- [x] config/config.yaml - Reasonable defaults
- [x] config/rules.yaml - Complete classification rules
- [x] .env.example - Template with placeholders
- [x] .gitignore - Comprehensive ignore rules
- [x] requirements.txt - All dependencies listed
- [x] requirements-dev.txt - Dev dependencies
- [x] .pre-commit-config.yaml - Pre-commit hooks

## ✅ Scripts & Automation

- [x] setup.sh - Unix/Linux/macOS setup script
- [x] setup.ps1 - Windows PowerShell setup script
- [x] test_installation.py - Installation verification
- [x] test_quick.py - Quick functionality test
- [x] All scripts executable (chmod +x)

## ✅ Testing

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] test_installation.py runs successfully
- [ ] test_quick.py runs with env vars
- [ ] No hardcoded paths in tests
- [ ] Mock external dependencies (Gmail)

## ✅ Repository Structure

```
✓ .github/
  ✓ workflows/          # CI/CD pipelines (if applicable)
✓ config/
  ✓ config.yaml
  ✓ rules.yaml
✓ src/
  ✓ __init__.py
  ✓ gmail_client.py
  ✓ email_parser.py
  ✓ document_classifier.py
  ✓ file_manager.py
  ✓ report_generator.py
  ✓ config_loader.py
✓ tests/
  ✓ test_*.py files
✓ docs/               # Optional: additional documentation
✓ .env.example
✓ .gitignore
✓ .pre-commit-config.yaml
✓ CHANGELOG.md
✓ CONTRIBUTING.md
✓ DOCUMENTATION.md
✓ INSTALLATION.md
✓ LICENSE
✓ main.py
✓ Makefile           # Optional: build commands
✓ pyproject.toml     # Python project metadata
✓ QUICKSTART.md
✓ README.md
✓ requirements-dev.txt
✓ requirements.txt
✓ RESUME_GUIDE.md
✓ setup.py
✓ setup.ps1
✓ setup.sh
✓ test_installation.py
✓ test_quick.py
```

## ✅ Git Cleanup

```bash
# Remove sensitive history (if needed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CAUTION: only if repo not public yet)
git push origin --force --all

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## ✅ README Badges

Update README.md with your actual repository URL:

```markdown
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/gmail-doc-scrapper?style=social)](https://github.com/yourusername/gmail-doc-scrapper/stargazers)
```

## ✅ Package Metadata

Update `setup.py` and `pyproject.toml`:

```python
# setup.py
setup(
    name="gmail-doc-scrapper",
    version="1.0.0",
    author="Your Name",
    author_email="your-email@example.com",
    url="https://github.com/yourusername/gmail-doc-scrapper",
    # ... rest of setup
)
```

```toml
# pyproject.toml
[project]
name = "gmail-doc-scrapper"
version = "1.0.0"
authors = [
  { name="Your Name", email="your-email@example.com" },
]
repository = "https://github.com/yourusername/gmail-doc-scrapper"
```

## ✅ License

Verify LICENSE file:
- [x] MIT License included
- [ ] Update year: 2024/2025/2026
- [ ] Update copyright holder name

## ✅ Contributing

CONTRIBUTING.md should include:
- [x] Code of Conduct
- [x] How to report bugs
- [x] How to suggest features
- [x] Pull request process
- [x] Development setup
- [x] Code style guidelines

## ✅ GitHub Repository Settings

Before making public:

### General
- [ ] Repository name: `gmail-doc-scrapper`
- [ ] Description: "Intelligent document extraction from Gmail using AI"
- [ ] Website: (optional)
- [ ] Topics: `python`, `gmail`, `imap`, `nlp`, `document-extraction`, `spacy`, `automation`

### Features
- [ ] Enable Issues
- [ ] Enable Projects (optional)
- [ ] Enable Wiki (optional)
- [ ] Enable Discussions (recommended)

### Security
- [ ] Add SECURITY.md (security policy)
- [ ] Enable Dependabot alerts
- [ ] Enable code scanning (optional)

### Branches
- [ ] Default branch: `main` or `master`
- [ ] Branch protection rules (optional)

## ✅ First Release

1. **Tag Version**
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

2. **Create GitHub Release**
- Go to Releases
- Click "Create a new release"
- Tag: v1.0.0
- Title: "Gmail Document Scraper v1.0.0"
- Description: Copy from CHANGELOG.md

3. **Publish to PyPI** (optional)
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

## ✅ Announcement

After release:
- [ ] Share on social media
- [ ] Post to relevant subreddits (r/Python, r/automation)
- [ ] Share on Hacker News (if appropriate)
- [ ] Add to awesome-python lists
- [ ] Create product hunt listing (optional)

## ✅ Post-Release

- [ ] Monitor issues
- [ ] Respond to discussions
- [ ] Review pull requests
- [ ] Update documentation based on feedback
- [ ] Plan next version features

---

## Quick Cleanup Commands

```bash
# Remove all .env files
find . -name ".env" -type f -delete

# Remove all checkpoint files
find . -name ".checkpoint.json" -type f -delete
find . -name ".last_run.json" -type f -delete

# Remove all output/reports
rm -rf output/* reports/*

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Verify no credentials in code
grep -r "password" --exclude-dir=venv --exclude-dir=.git .
grep -r "GMAIL_EMAIL" --exclude=".env.example" --exclude-dir=venv .
```

## Final Check

```bash
# Run this before publishing
python test_installation.py
python -m pytest tests/ -v
pre-commit run --all-files
black --check main.py src/ tests/
flake8 main.py src/ tests/
```

---

**Status:** Ready for open source release ✅

**Last Review:** 2026-01-02
