#!/usr/bin/env python3
"""Gmail Document Scraper - Main CLI entry point."""

import sys
import email.utils
import tempfile
import os
import getpass
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

from src.config_loader import ConfigLoader
from src.gmail_client import GmailClient
from src.email_parser import EmailParser
from src.document_classifier import DocumentClassifier
from src.file_manager import FileManager
from src.report_generator import ReportGenerator

console = Console()

# File to store last run configuration
LAST_RUN_FILE = Path("./reports/.last_run.json")


def save_run_config(gmail_email, start_date, end_date, document_types, folder, output_dir, dry_run):
    """Save run configuration for resume functionality.

    Args:
        gmail_email: Gmail email address
        start_date: Start date for email search
        end_date: End date for email search
        document_types: Document types filter
        folder: Gmail folder(s) to search
        output_dir: Output directory path
        dry_run: Whether this is a dry run
    """
    import json

    config = {
        'gmail_email': gmail_email,
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'document_types': document_types,
        'folder': folder,
        'output_dir': output_dir,
        'dry_run': dry_run,
        'saved_at': datetime.now().isoformat()
    }

    LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_run_config():
    """Load last run configuration for resume.

    Returns:
        Tuple of (gmail_email, start_date, end_date, document_types, folder, output_dir, dry_run)
        or None if no saved config exists
    """
    import json

    if not LAST_RUN_FILE.exists():
        return None

    try:
        with open(LAST_RUN_FILE, 'r') as f:
            config = json.load(f)

        start_date = datetime.fromisoformat(config['start_date']) if config['start_date'] else None
        end_date = datetime.fromisoformat(config['end_date']) if config['end_date'] else None

        return (
            config['gmail_email'],
            start_date,
            end_date,
            config['document_types'],
            config['folder'],
            config['output_dir'],
            config['dry_run']
        )
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load saved run configuration: {e}[/yellow]")
        return None


def check_dependencies(config):
    """Check all required and optional dependencies before starting.

    Args:
        config: ConfigLoader instance with loaded configuration

    Returns:
        Tuple of (all_ok: bool, warnings: list)
    """
    warnings = []
    critical_errors = []

    console.print("\n[cyan]Checking dependencies...[/cyan]")

    # Check spaCy and Portuguese model
    try:
        import spacy
        try:
            nlp = spacy.load("pt_core_news_lg")
            console.print("[green]✓ spaCy and pt_core_news_lg model found[/green]")
        except OSError:
            warnings.append("spaCy Portuguese model (pt_core_news_lg) not installed")
            console.print("[yellow]⚠ spaCy model not found. Install with:[/yellow]")
            console.print("[yellow]  python -m spacy download pt_core_news_lg[/yellow]")
            console.print("[yellow]  Classification will use pattern/keyword matching only[/yellow]")
    except ImportError:
        warnings.append("spaCy not installed")
        console.print("[yellow]⚠ spaCy not installed. Install with:[/yellow]")
        console.print("[yellow]  pip install spacy[/yellow]")
        console.print("[yellow]  Classification will use pattern/keyword matching only[/yellow]")

    # Check scikit-learn (optional for ML features)
    if config.get('classification.use_ml_model'):
        try:
            import sklearn
            console.print("[green]✓ scikit-learn found[/green]")
        except ImportError:
            warnings.append("scikit-learn not installed (ML features disabled)")
            console.print("[yellow]⚠ scikit-learn not installed. Install with:[/yellow]")
            console.print("[yellow]  pip install scikit-learn[/yellow]")
            console.print("[yellow]  ML-based classification will be disabled[/yellow]")

    # Check OCR dependencies (only if OCR is enabled)
    if config.get('processing.enable_ocr'):
        ocr_available = True
        try:
            import pytesseract
            console.print("[green]✓ pytesseract found[/green]")
        except ImportError:
            ocr_available = False
            warnings.append("pytesseract not installed (OCR disabled)")
            console.print("[yellow]⚠ pytesseract not installed. Install with:[/yellow]")
            console.print("[yellow]  pip install pytesseract[/yellow]")

        try:
            import pdf2image
            console.print("[green]✓ pdf2image found[/green]")
        except ImportError:
            ocr_available = False
            warnings.append("pdf2image not installed (OCR disabled)")
            console.print("[yellow]⚠ pdf2image not installed. Install with:[/yellow]")
            console.print("[yellow]  pip install pdf2image[/yellow]")

        if not ocr_available:
            console.print("[yellow]  OCR for scanned documents will not work[/yellow]")

    # Check core PDF processing libraries
    try:
        import PyPDF2
        console.print("[green]✓ PyPDF2 found[/green]")
    except ImportError:
        critical_errors.append("PyPDF2 not installed")
        console.print("[red]✗ PyPDF2 not installed (REQUIRED). Install with:[/red]")
        console.print("[red]  pip install PyPDF2[/red]")

    try:
        import pdfplumber
        console.print("[green]✓ pdfplumber found[/green]")
    except ImportError:
        critical_errors.append("pdfplumber not installed")
        console.print("[red]✗ pdfplumber not installed (REQUIRED). Install with:[/red]")
        console.print("[red]  pip install pdfplumber[/red]")

    console.print()

    if critical_errors:
        console.print("[red]❌ Critical dependencies missing. Please install them before continuing.[/red]\n")
        return False, warnings

    if warnings:
        console.print(f"[yellow]⚠ Found {len(warnings)} optional dependency issue(s).[/yellow]")
        console.print("[yellow]  Application will run with limited functionality.[/yellow]\n")

        proceed = Confirm.ask("[cyan]Continue anyway?[/cyan]", default=True)
        if not proceed:
            return False, warnings
    else:
        console.print("[green]✓ All dependencies OK[/green]\n")

    return True, warnings


def interactive_mode(config_dir):
    """Run interactive mode to collect user inputs.

    Args:
        config_dir: Configuration directory path

    Returns:
        Tuple of (gmail_email, gmail_password, start_date, end_date, document_types, folder, output_dir, dry_run)
    """
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("Please provide the following information:\n")

    # Gmail credentials
    gmail_email = Prompt.ask("[cyan]Gmail email address[/cyan]")
    console.print("[yellow]Enter your Gmail App Password (input will be hidden)[/yellow]")
    gmail_password = getpass.getpass("Gmail App Password: ")

    # Date range
    console.print("\n[cyan]Date Range Configuration[/cyan]")
    default_start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    start_date_str = Prompt.ask(
        "[cyan]Start date (YYYY-MM-DD)[/cyan]",
        default=default_start
    )
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    use_end_date = Confirm.ask("[cyan]Do you want to specify an end date?[/cyan]", default=False)
    end_date = None
    if use_end_date:
        end_date_str = Prompt.ask("[cyan]End date (YYYY-MM-DD)[/cyan]")
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Document types
    console.print("\n[cyan]Available Document Types:[/cyan]")
    try:
        # Load rules to show available document types
        from pathlib import Path
        import yaml
        rules_path = Path(config_dir) / "rules.yaml"
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)

        # Display available document types in a table
        table = Table(title="Document Types")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="green")

        for doc_type, config in rules.items():
            table.add_row(doc_type, config.get('display_name', doc_type))

        console.print(table)
        console.print()
    except Exception as e:
        console.print(f"[yellow]Could not load document types: {e}[/yellow]")

    filter_types = Confirm.ask("[cyan]Do you want to filter by specific document types?[/cyan]", default=False)
    document_types = None
    if filter_types:
        document_types = Prompt.ask(
            "[cyan]Enter document type IDs (comma-separated, e.g., invoices,contracts)[/cyan]"
        )

    # Auto-detect All Mail folder
    folder = None  # Will be auto-detected
    console.print("\n[cyan]📁 Will auto-detect 'All Mail' folder (contains all emails)[/cyan]")

    # Output directory
    console.print("\n[cyan]Output Configuration[/cyan]")
    use_custom_output = Confirm.ask("[cyan]Use custom output directory?[/cyan]", default=False)
    output_dir = None
    if use_custom_output:
        output_dir = Prompt.ask("[cyan]Output directory path[/cyan]", default="./output")
        # Strip quotes if user included them
        output_dir = output_dir.strip('"').strip("'")

    # Dry run
    dry_run = Confirm.ask("\n[cyan]Run in dry-run mode (no files will be saved)?[/cyan]", default=False)

    # Summary and confirmation
    console.print("\n[bold cyan]Configuration Summary:[/bold cyan]")
    console.print(f"  Email: [green]{gmail_email}[/green]")
    console.print(f"  Start Date: [green]{start_date.strftime('%Y-%m-%d')}[/green]")
    console.print(f"  End Date: [green]{end_date.strftime('%Y-%m-%d') if end_date else 'Not specified'}[/green]")
    console.print(f"  Document Types: [green]{document_types if document_types else 'All types'}[/green]")
    console.print(f"  Folder: [green]All Mail (auto-detect)[/green]")
    console.print(f"  Output Directory: [green]{output_dir if output_dir else 'Default (./output)'}[/green]")
    console.print(f"  Dry Run: [green]{dry_run}[/green]")
    console.print()

    if not Confirm.ask("[bold cyan]Proceed with these settings?[/bold cyan]", default=True):
        console.print("[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)

    return gmail_email, gmail_password, start_date, end_date, document_types, folder, output_dir, dry_run


@click.command()
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Run in interactive mode with prompts for all settings'
)
@click.option(
    '--start-date',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='Start date for email search (YYYY-MM-DD)',
    required=False
)
@click.option(
    '--end-date',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='End date for email search (YYYY-MM-DD)',
    required=False
)
@click.option(
    '--document-types',
    type=str,
    help='Comma-separated list of document types to extract (e.g., invoices,contracts)',
    required=False
)
@click.option(
    '--folder',
    type=str,
    default=None,
    help='Gmail folder to search (default: auto-detect All Mail folder)'
)
@click.option(
    '--config-dir',
    type=click.Path(exists=True),
    default='config',
    help='Configuration directory path'
)
@click.option(
    '--output-dir',
    type=str,
    help='Output directory for extracted documents',
    required=False
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Run without saving files (for testing)'
)
@click.option(
    '--resume',
    is_flag=True,
    help='Resume from last run (uses saved configuration and checkpoint)'
)
def main(interactive, start_date, end_date, document_types, folder, config_dir, output_dir, dry_run, resume):
    """Gmail Document Scraper - Intelligent document extraction from Gmail.

    Extracts and classifies documents (invoices, contracts, etc.) from Gmail
    using AI-powered content analysis.

    Examples:

        # Run in interactive mode
        python main.py --interactive

        # Extract all documents from last 30 days
        python main.py --start-date 2024-12-01

        # Extract only invoices from specific period
        python main.py --start-date 2024-01-01 --end-date 2024-12-31 --document-types invoices

        # Dry run to test configuration
        python main.py --start-date 2024-12-01 --dry-run
    """
    console.print("[bold cyan]Gmail Document Scraper v2.0[/bold cyan]\n")

    # Handle resume mode
    if resume:
        console.print("[cyan]Resume mode activated - loading saved configuration...[/cyan]")
        saved_config = load_run_config()

        if saved_config:
            gmail_email, start_date, end_date, document_types, folder, output_dir, dry_run = saved_config

            # Load password from environment
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            if not gmail_password:
                console.print("[yellow]Gmail App Password not found in environment[/yellow]")
                gmail_password = getpass.getpass("Gmail App Password: ")

            # Set environment variables
            os.environ['GMAIL_EMAIL'] = gmail_email
            os.environ['GMAIL_APP_PASSWORD'] = gmail_password
            if output_dir:
                os.environ['OUTPUT_DIR'] = output_dir

            # Display loaded configuration
            console.print("[green]✓ Configuration loaded from last run:[/green]")
            console.print(f"  Email: {gmail_email}")
            console.print(f"  Start: {start_date.strftime('%Y-%m-%d') if start_date else 'None'}")
            console.print(f"  End: {end_date.strftime('%Y-%m-%d') if end_date else 'None'}")
            console.print(f"  Types: {document_types or 'All'}")
            console.print(f"  Folder: {folder}")
            console.print()

            # Check for checkpoint
            checkpoint_file = Path("./reports/.checkpoint.json")
            if checkpoint_file.exists():
                import json
                try:
                    with open(checkpoint_file, 'r') as f:
                        checkpoint_data = json.load(f)
                    console.print(f"[green]✓ Found checkpoint: {len(checkpoint_data.get('processed', []))} emails already processed[/green]\n")
                except Exception:
                    pass
        else:
            console.print("[red]No saved configuration found. Cannot resume.[/red]")
            console.print("[yellow]Run with --interactive first, then use --resume for subsequent runs.[/yellow]")
            sys.exit(1)

    # Handle interactive mode
    elif interactive:
        gmail_email, gmail_password, start_date, end_date, document_types, folder, output_dir, dry_run = interactive_mode(config_dir)
        # Temporarily set environment variables for this session
        os.environ['GMAIL_EMAIL'] = gmail_email
        os.environ['GMAIL_APP_PASSWORD'] = gmail_password
        if output_dir:
            os.environ['OUTPUT_DIR'] = output_dir

    # Handle output directory if specified
    if output_dir and not interactive and not resume:
        os.environ['OUTPUT_DIR'] = output_dir

    if dry_run:
        console.print("[yellow]WARNING: DRY RUN MODE - No files will be saved[/yellow]\n")

    try:
        # Load configuration
        console.print("[cyan]Loading configuration...[/cyan]")
        config = ConfigLoader(config_dir)
        console.print("[green]Configuration loaded successfully[/green]")

        # Check dependencies
        deps_ok, deps_warnings = check_dependencies(config)
        if not deps_ok:
            console.print("[red]Cannot continue due to missing dependencies.[/red]")
            sys.exit(1)

        # Clean output directory before starting (skip if resuming)
        output_dir_path = Path(config.get('output.base_dir', './output'))
        checkpoint_file = Path("./reports/.checkpoint.json")

        if not resume:
            # Only clean if NOT resuming
            if output_dir_path.exists():
                console.print(f"[yellow]Cleaning output directory: {output_dir_path}[/yellow]")
                try:
                    shutil.rmtree(output_dir_path)
                    console.print("[green]✓ Output directory cleaned[/green]")

                    # Also clean checkpoint to start fresh
                    if checkpoint_file.exists():
                        checkpoint_file.unlink()
                        console.print("[green]✓ Checkpoint cleaned (starting fresh)[/green]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not fully clean output directory: {e}[/yellow]")
        else:
            console.print("[cyan]Resume mode: Keeping existing output directory and checkpoint[/cyan]")

        output_dir_path.mkdir(parents=True, exist_ok=True)
        console.print()

        # Parse document types filter
        doc_types_filter = None
        if document_types:
            doc_types_filter = [dt.strip() for dt in document_types.split(',')]
            console.print(f"[cyan]Filtering document types: {', '.join(doc_types_filter)}[/cyan]\n")

        # Initialize components
        gmail_client = GmailClient(
            email_address=config.gmail_email,
            password=config.gmail_password,
            server=config.get('imap.server'),
            port=config.get('imap.port')
        )

        email_parser = EmailParser(
            supported_extensions=config.get('processing.supported_extensions')
        )

        classifier = DocumentClassifier(config.config, config.rules)

        file_manager = FileManager(config.config)

        report = ReportGenerator(config.config)

        # Connect to Gmail
        console.print()
        if not gmail_client.connect():
            console.print("[red]Failed to connect to Gmail. Exiting.[/red]")
            sys.exit(1)

        # Save run configuration for future resume (only in interactive or first run)
        if interactive or not resume:
            try:
                save_run_config(
                    gmail_email=os.getenv('GMAIL_EMAIL'),
                    start_date=start_date,
                    end_date=end_date,
                    document_types=document_types,
                    folder=folder,
                    output_dir=output_dir,
                    dry_run=dry_run
                )
                console.print("[dim]✓ Run configuration saved (use --resume to continue later)[/dim]")
            except Exception as e:
                console.print(f"[dim yellow]Warning: Could not save run configuration: {e}[/dim yellow]")

        console.print()

        # Auto-detect and select All Mail folder
        all_mail_folder = gmail_client.find_all_mail_folder()
        if not all_mail_folder:
            console.print("[red]❌ Could not find 'All Mail' folder in your Gmail account.[/red]")
            console.print("[yellow]This might be due to localization or Gmail configuration.[/yellow]")
            gmail_client.disconnect()
            sys.exit(1)

        console.print(f"[cyan]Selecting folder: {all_mail_folder}[/cyan]")
        if not gmail_client.select_folder(all_mail_folder):
            console.print(f"[red]Failed to select folder '{all_mail_folder}'. Exiting.[/red]")
            gmail_client.disconnect()
            sys.exit(1)

        console.print(f"[green]✓ Connected to '{all_mail_folder}'[/green]")
        console.print()

        # Search emails in All Mail
        email_ids = gmail_client.search_emails(
            start_date=start_date,
            end_date=end_date,
            has_attachments=False
        )

        if not email_ids:
            console.print("[yellow]No emails found matching the specified criteria[/yellow]")
            gmail_client.disconnect()
            sys.exit(0)

        console.print()

        # Load checkpoint if exists (checkpoint_file defined earlier during cleanup)
        processed_ids = set()
        if checkpoint_file.exists():
            try:
                import json
                with open(checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
                    processed_ids = set(checkpoint_data.get('processed', []))
                    console.print(f"[cyan]Found checkpoint: {len(processed_ids)} emails already processed[/cyan]")
            except Exception:
                pass

        # Filter out already processed emails
        remaining_ids = [eid for eid in email_ids if eid.decode() not in processed_ids]
        if len(remaining_ids) < len(email_ids):
            console.print(f"[green]Skipping {len(email_ids) - len(remaining_ids)} already processed emails[/green]")

        console.print()

        # Process emails
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                f"[cyan]Processing {len(remaining_ids)} emails...",
                total=len(remaining_ids)
            )

            email_count = 0
            failed_fetches = 0  # Track consecutive failed fetches

            for email_id in remaining_ids:
                email_count += 1

                # Log progress and save checkpoint every 100 emails
                if email_count % 100 == 0:
                    console.print(f"\n[cyan]═══ Progress: {email_count}/{len(remaining_ids)} emails processed ═══[/cyan]")
                    console.print(f"[cyan]Connection status: {'✓ Connected' if gmail_client.connection else '✗ Disconnected'}[/cyan]")
                    console.print(f"[cyan]Checkpoint size: {len(processed_ids)} emails marked as processed[/cyan]")
                    console.print(f"[cyan]Failed fetches: {failed_fetches} consecutive[/cyan]")

                    # Save checkpoint
                    try:
                        import json
                        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(checkpoint_file, 'w') as f:
                            json.dump({'processed': list(processed_ids), 'total_processed': len(processed_ids)}, f)
                        console.print(f"[dim]  ✓ Checkpoint saved: {len(processed_ids)} emails[/dim]\n")
                    except Exception as e:
                        console.print(f"[yellow]  Warning: Could not save checkpoint: {e}[/yellow]\n")

                try:
                    # Adaptive delay based on failure rate
                    import time
                    base_delay = 0.5  # Increased from 0.3 to 0.5 for more conservative rate

                    # Add progressive backoff if failures detected
                    if failed_fetches > 0:
                        backoff_delay = min(failed_fetches * 0.1, 5.0)  # Max 5s backoff
                        time.sleep(base_delay + backoff_delay)
                    else:
                        time.sleep(base_delay)

                    # Fetch email (enable verbose logging after 10 failures to debug)
                    verbose = (failed_fetches >= 10)
                    msg = gmail_client.fetch_email(email_id, verbose=verbose)
                    if not msg:
                        failed_fetches += 1

                        # Progressive intervention based on failure count
                        if failed_fetches == 20:
                            console.print(f"\n[yellow]⚠ 20 consecutive failures - adding 5s cooldown[/yellow]")
                            time.sleep(5)
                        elif failed_fetches == 50:
                            console.print(f"\n[yellow]⚠ 50 consecutive failures - trying reconnection[/yellow]")
                            if gmail_client.reconnect(max_attempts=3):
                                console.print("[green]✓ Reconnected[/green]\n")
                                failed_fetches = 0
                            else:
                                console.print("[yellow]Reconnection failed, continuing with backoff[/yellow]")
                        elif failed_fetches == 75:
                            console.print(f"\n[yellow]⚠ 75 consecutive failures - adding 30s cooldown[/yellow]")
                            time.sleep(30)

                        # Check if connection is lost - try to recover
                        if not gmail_client.connection:
                            console.print(f"\n[yellow]Connection lost (failed fetches: {failed_fetches}), attempting manual reconnection...[/yellow]")

                            # Try to reconnect (10 attempts, ~3 minutes total)
                            if gmail_client.reconnect(max_attempts=10):
                                console.print("[green]✓ Reconnected! Continuing...[/green]\n")
                                # Mark as processed to avoid reprocessing
                                processed_ids.add(email_id.decode())
                                failed_fetches = 0  # Reset counter
                                continue
                            else:
                                console.print("\n[red]❌ Unable to reconnect after multiple attempts[/red]")
                                console.print(f"[yellow]Processed {email_count}/{len(remaining_ids)} emails before permanent disconnect[/yellow]")
                                console.print(f"[yellow]Failed to fetch {failed_fetches} emails consecutively[/yellow]")
                                console.print("[yellow]Progress saved via checkpoint - you can resume later[/yellow]")
                                break

                        # Check if too many consecutive failures (possible Gmail issue)
                        if failed_fetches >= 100:
                            console.print(f"\n[red]❌ Too many consecutive fetch failures ({failed_fetches})[/red]")
                            console.print("[red]This usually means Gmail is rate limiting or there's a connection issue[/red]")
                            console.print(f"[yellow]Processed {email_count}/{len(remaining_ids)} emails[/yellow]")
                            console.print("[yellow]Recommendation: Wait 15-30 minutes, then run: python main.py --resume[/yellow]")
                            console.print("[yellow]Progress saved via checkpoint[/yellow]")
                            break

                        # Mark as processed even if fetch failed (email deleted, moved, etc.)
                        processed_ids.add(email_id.decode())
                        continue

                    # Reset failed counter on successful fetch
                    failed_fetches = 0

                    report.record_email_processed()

                    # Parse email
                    email_data = email_parser.parse_email(msg)

                    # NEW LOGIC: Classify based on email subject + body
                    console.print(f"\n[cyan]┌─ Processing email: {email_data['subject'][:60]}...[/cyan]")
                    console.print(f"[cyan]│  From: {email_data['from']}[/cyan]")
                    console.print(f"[cyan]│  Date: {email_data['date']}[/cyan]")

                    # Classify email content
                    result = classifier.classify_email(
                        subject=email_data['subject'],
                        body=email_data['body']
                    )

                    if not result:
                        console.print(f"[yellow]└─ Email not classified (no match)[/yellow]\n")
                        # Mark as processed and continue
                        processed_ids.add(email_id.decode())
                        progress.advance(task)
                        continue

                    console.print(f"[green]└─ Email classified as: {result.display_name} ({result.confidence:.0%})[/green]\n")

                    # Filter by document type if specified
                    if doc_types_filter and result.document_type not in doc_types_filter:
                        processed_ids.add(email_id.decode())
                        progress.advance(task)
                        continue

                    report.record_classified(result.document_type)

                    # Check if email has attachments
                    if not email_data['attachments']:
                        console.print(f"[yellow]  ⚠ Email classified but no attachments found[/yellow]\n")
                        processed_ids.add(email_id.decode())
                        progress.advance(task)
                        continue

                    report.record_attachment_found(True)

                    # Filter attachments by size
                    attachments = email_parser.filter_attachments_by_size(
                        email_data['attachments'],
                        config.get('processing.max_file_size_mb')
                    )

                    console.print(f"[cyan]  → Saving {len(attachments)} attachment(s) to '{result.document_type}' folder...[/cyan]")

                    # Save ALL attachments to the classified document type folder
                    for attachment in attachments:
                        try:
                            console.print(f"[cyan]    • {attachment.filename} ({attachment.size / 1024:.1f}KB)[/cyan]")

                            # Save file (unless dry run)
                            if not dry_run:
                                email_metadata = {
                                    'subject': email_data['subject'],
                                    'from': email_data['from'],
                                    'date': email.utils.parsedate_to_datetime(email_data['date'])
                                }

                                output_path = file_manager.save_file(
                                    content=attachment.content,
                                    document_type=result.document_type,
                                    original_filename=attachment.filename,
                                    email_metadata=email_metadata,
                                    classification_confidence=result.confidence
                                )

                                if output_path:
                                    report.record_saved(result.document_type)
                                    console.print(f"[green]      ✓ Saved: {output_path}[/green]")
                                else:
                                    report.record_duplicate()
                                    console.print(f"[yellow]      ⚠ Duplicate (skipped)[/yellow]")
                            else:
                                console.print(
                                    f"[yellow]      DRY RUN: Would save {attachment.filename} "
                                    f"to {result.document_type}[/yellow]"
                                )

                        except Exception as e:
                            error_msg = f"Error saving attachment {attachment.filename}: {e}"
                            report.record_error(error_msg)
                            console.print(f"[red]      ✗ {error_msg}[/red]")

                    console.print()  # Add spacing after processing email

                    # Mark email as processed
                    processed_ids.add(email_id.decode())

                except Exception as e:
                    error_msg = f"Error processing email {email_id}: {e}"
                    report.record_error(error_msg)
                    # Still mark as processed to avoid reprocessing
                    processed_ids.add(email_id.decode())

                progress.advance(task)

        # Log why loop ended
        console.print(f"\n[cyan]Loop ended: Processed {email_count}/{len(remaining_ids)} emails[/cyan]")
        if email_count >= len(remaining_ids):
            console.print("[green]✓ All emails processed successfully[/green]")
        else:
            console.print(f"[yellow]⚠ Loop ended early - {len(remaining_ids) - email_count} emails not processed[/yellow]")

        # Save final checkpoint
        try:
            import json
            with open(checkpoint_file, 'w') as f:
                json.dump({'processed': list(processed_ids)}, f)
            console.print(f"[green]✓ Final checkpoint saved: {len(processed_ids)} emails processed[/green]")
        except Exception:
            pass

        # Disconnect
        gmail_client.disconnect()

        console.print("\n")

        # Generate report
        report.generate_report()

        # Show LLM add-on information
        console.print("\n")
        console.print("[cyan]═══════════════════════════════════════════════════════════[/cyan]")
        console.print("[bold yellow]⚠️  Classification Limitations[/bold yellow]")
        console.print("[white]This tool uses rule-based classification (~85-90% accuracy)[/white]")
        console.print("\n[bold cyan]🚀 Need Better Results?[/bold cyan]")
        console.print("[white]LLM-powered add-on available with:[/white]")
        console.print("  [green]✓[/green] 95%+ accuracy (GPT-4/Claude)")
        console.print("  [green]✓[/green] Advanced metadata extraction")
        console.print("  [green]✓[/green] CSV/Excel export")
        console.print("  [green]✓[/green] 30+ languages support")
        console.print("\n[bold]Contact:[/bold] [link=mailto:joao.fernandes@docdigitizer.com]joao.fernandes@docdigitizer.com[/link]")
        console.print("[cyan]═══════════════════════════════════════════════════════════[/cyan]")
        console.print()

        # Clean up checkpoint file if all emails were processed
        if len(processed_ids) >= len(email_ids):
            try:
                checkpoint_file.unlink()
                console.print("[dim]✓ Checkpoint cleaned (all emails processed)[/dim]")
            except Exception:
                pass

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
