#!/usr/bin/env python3
"""Test script to verify Gmail Document Scraper installation."""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_python_version():
    """Test Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)"


def test_import(module_name, package_name=None):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        return True, "OK"
    except ImportError as e:
        pkg = package_name or module_name
        return False, f"Missing (pip install {pkg})"


def main():
    """Run installation tests."""
    console.print(Panel.fit(
        "[bold cyan]Gmail Document Scraper - Installation Test[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Create results table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=30)
    table.add_column("Status", width=40)
    table.add_column("Result", justify="center", width=10)

    all_passed = True

    # Test Python version
    passed, msg = test_python_version()
    all_passed &= passed
    table.add_row(
        "Python Version",
        msg,
        "[green]✓[/green]" if passed else "[red]✗[/red]"
    )

    # Test required modules
    modules = [
        ("dotenv", "python-dotenv"),
        ("yaml", "pyyaml"),
        ("click", "click"),
        ("rich", "rich"),
        ("spacy", "spacy"),
        ("sklearn", "scikit-learn"),
        ("PyPDF2", "PyPDF2"),
        ("pdfplumber", "pdfplumber"),
        ("docx", "python-docx"),
        ("openpyxl", "openpyxl"),
        ("PIL", "Pillow"),
    ]

    for module, package in modules:
        passed, msg = test_import(module, package)
        all_passed &= passed
        table.add_row(
            f"Module: {module}",
            msg,
            "[green]✓[/green]" if passed else "[red]✗[/red]"
        )

    # Test spaCy model
    try:
        import spacy
        nlp = spacy.load("pt_core_news_lg")
        table.add_row(
            "spaCy Portuguese Model",
            "pt_core_news_lg loaded",
            "[green]✓[/green]"
        )
    except OSError:
        all_passed = False
        table.add_row(
            "spaCy Portuguese Model",
            "Not found (python -m spacy download pt_core_news_lg)",
            "[red]✗[/red]"
        )
    except ImportError:
        pass  # Already reported above

    # Test project structure
    from pathlib import Path

    files = [
        "main.py",
        "config/config.yaml",
        "config/rules.yaml",
        "src/__init__.py",
        "src/config_loader.py",
        "src/gmail_client.py",
        "src/email_parser.py",
        "src/document_classifier.py",
        "src/file_manager.py",
        "src/report_generator.py",
    ]

    for file_path in files:
        exists = Path(file_path).exists()
        all_passed &= exists
        table.add_row(
            f"File: {file_path}",
            "Found" if exists else "Missing",
            "[green]✓[/green]" if exists else "[red]✗[/red]"
        )

    console.print(table)
    console.print()

    if all_passed:
        console.print(Panel.fit(
            "[bold green]✓ All tests passed![/bold green]\n"
            "The installation is complete and ready to use.\n\n"
            "Next step: python main.py --interactive",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel.fit(
            "[bold red]✗ Some tests failed[/bold red]\n"
            "Please install missing dependencies:\n\n"
            "pip install -r requirements.txt\n"
            "python -m spacy download pt_core_news_lg",
            border_style="red"
        ))
        return 1


if __name__ == "__main__":
    sys.exit(main())
