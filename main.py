#!/usr/bin/env python3
"""Gmail Document Scraper - Main CLI entry point."""

import sys
import email.utils
import tempfile
import os
import getpass
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

    # Gmail folder
    console.print("\n[cyan]Gmail Folder Configuration[/cyan]")
    folder = Prompt.ask(
        "[cyan]Gmail folder to search[/cyan]",
        default="INBOX"
    )

    # Output directory
    console.print("\n[cyan]Output Configuration[/cyan]")
    use_custom_output = Confirm.ask("[cyan]Use custom output directory?[/cyan]", default=False)
    output_dir = None
    if use_custom_output:
        output_dir = Prompt.ask("[cyan]Output directory path[/cyan]", default="./output")

    # Dry run
    dry_run = Confirm.ask("\n[cyan]Run in dry-run mode (no files will be saved)?[/cyan]", default=False)

    # Summary and confirmation
    console.print("\n[bold cyan]Configuration Summary:[/bold cyan]")
    console.print(f"  Email: [green]{gmail_email}[/green]")
    console.print(f"  Start Date: [green]{start_date.strftime('%Y-%m-%d')}[/green]")
    console.print(f"  End Date: [green]{end_date.strftime('%Y-%m-%d') if end_date else 'Not specified'}[/green]")
    console.print(f"  Document Types: [green]{document_types if document_types else 'All types'}[/green]")
    console.print(f"  Folder: [green]{folder}[/green]")
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
    default='INBOX',
    help='Gmail folder to search (default: INBOX)'
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
def main(interactive, start_date, end_date, document_types, folder, config_dir, output_dir, dry_run):
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
    console.print("[bold cyan]Gmail Document Scraper v1.0[/bold cyan]\n")

    # Handle interactive mode
    if interactive:
        gmail_email, gmail_password, start_date, end_date, document_types, folder, output_dir, dry_run = interactive_mode(config_dir)
        # Temporarily set environment variables for this session
        os.environ['GMAIL_EMAIL'] = gmail_email
        os.environ['GMAIL_APP_PASSWORD'] = gmail_password
        if output_dir:
            os.environ['OUTPUT_DIR'] = output_dir

    # Handle output directory if specified
    if output_dir and not interactive:
        os.environ['OUTPUT_DIR'] = output_dir

    if dry_run:
        console.print("[yellow]WARNING: DRY RUN MODE - No files will be saved[/yellow]\n")

    try:
        # Load configuration
        console.print("[cyan]Loading configuration...[/cyan]")
        config = ConfigLoader(config_dir)
        console.print("[green]Configuration loaded successfully[/green]\n")

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

        console.print()

        # Select folder
        if not gmail_client.select_folder(folder):
            console.print(f"[red]Failed to select folder '{folder}'. Exiting.[/red]")
            gmail_client.disconnect()
            sys.exit(1)

        console.print()

        # Search emails
        email_ids = gmail_client.search_emails(
            start_date=start_date,
            end_date=end_date,
            has_attachments=True
        )

        if not email_ids:
            console.print("[yellow]No emails found matching the specified criteria[/yellow]")
            gmail_client.disconnect()
            sys.exit(0)

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
                f"[cyan]Processing {len(email_ids)} emails...",
                total=len(email_ids)
            )

            for email_id in email_ids:
                try:
                    # Fetch email
                    msg = gmail_client.fetch_email(email_id)
                    if not msg:
                        continue

                    report.record_email_processed()

                    # Parse email
                    email_data = email_parser.parse_email(msg)

                    if not email_data['attachments']:
                        progress.advance(task)
                        continue

                    report.record_attachment_found(True)

                    # Filter attachments by size
                    attachments = email_parser.filter_attachments_by_size(
                        email_data['attachments'],
                        config.get('processing.max_file_size_mb')
                    )

                    # Process each attachment
                    for attachment in attachments:
                        try:
                            # Extract text from attachment
                            text_content = extract_text_from_bytes(
                                classifier,
                                attachment.content,
                                attachment.get_extension()
                            )

                            # Classify document
                            result = classifier.classify_document(
                                file_path=None,
                                text_content=text_content
                            )

                            if not result:
                                report.record_classification_failure()
                                continue

                            # Filter by document type if specified
                            if doc_types_filter and result.document_type not in doc_types_filter:
                                continue

                            report.record_classified(result.document_type)

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
                                else:
                                    report.record_duplicate()
                            else:
                                console.print(
                                    f"[yellow]DRY RUN: Would save {attachment.filename} "
                                    f"as {result.document_type}[/yellow]"
                                )

                        except Exception as e:
                            error_msg = f"Error processing attachment {attachment.filename}: {e}"
                            report.record_error(error_msg)
                            console.print(f"[red]{error_msg}[/red]")

                except Exception as e:
                    error_msg = f"Error processing email {email_id}: {e}"
                    report.record_error(error_msg)

                progress.advance(task)

        # Disconnect
        gmail_client.disconnect()

        console.print("\n")

        # Generate report
        report.generate_report()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def extract_text_from_bytes(classifier, content: bytes, extension: str) -> str:
    """Helper to extract text from attachment bytes.

    Args:
        classifier: DocumentClassifier instance
        content: File content as bytes
        extension: File extension

    Returns:
        Extracted text content
    """
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = classifier.extract_text(tmp_path)
        return text
    finally:
        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass


if __name__ == '__main__':
    main()
