# Contributing to Gmail Document Scraper

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://gitlab.com/your-username/gmail-doc-scraper/-/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach (optional)

### Contributing Code

1. **Fork the repository**

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

4. **Run tests**:
   ```bash
   pytest tests/
   black src/ tests/
   flake8 src/ tests/
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "feat: Add feature description"
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Merge Request**:
   - Provide clear description of changes
   - Reference related issues
   - Ensure CI pipeline passes

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 100 characters
- Use type hints where appropriate

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings:
  ```python
  def function(arg1: str, arg2: int) -> bool:
      """Short description.

      Longer description if needed.

      Args:
          arg1: Description of arg1
          arg2: Description of arg2

      Returns:
          Description of return value

      Raises:
          ValueError: When something goes wrong
      """
  ```

### Testing

- Write unit tests for new functionality
- Aim for >80% code coverage
- Use pytest fixtures for test setup
- Name tests clearly: `test_<functionality>_<condition>_<expected_result>`

### Git Workflow

- Keep commits atomic and focused
- Write clear commit messages
- Rebase on main before creating MR
- Squash commits if needed for cleaner history

## Project Structure

```
gmail-doc-scraper/
├── src/                    # Source code
│   ├── config_loader.py    # Configuration management
│   ├── gmail_client.py     # Gmail IMAP client
│   ├── email_parser.py     # Email parsing
│   ├── document_classifier.py  # Document classification
│   ├── file_manager.py     # File organization
│   └── report_generator.py # Reporting
├── config/                 # Configuration files
├── tests/                  # Test suite
├── main.py                 # CLI entry point
└── requirements.txt        # Dependencies
```

## Adding New Document Types

To add support for a new document type:

1. **Add to `config/rules.yaml`**:
   ```yaml
   new_type:
     display_name: "Display Name"
     keywords:
       - keyword1
       - keyword2
     patterns:
       - "regex_pattern"
     entities:
       - ENTITY_TYPE
     confidence_boost: 0.1
   ```

2. **Update tests** in `tests/test_document_classifier.py`

3. **Update documentation** in README.md

## Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```

2. Install pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. Run tests before committing:
   ```bash
   pytest tests/
   ```

## Questions?

- Open a discussion in [Issues](https://gitlab.com/your-username/gmail-doc-scraper/-/issues)
- Check existing documentation
- Ask in merge request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
