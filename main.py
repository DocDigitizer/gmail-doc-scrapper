#!/usr/bin/env python3
"""Gmail Document Scraper - Main CLI entry point."""

import sys
import email.utils
import tempfile
import os
from datetime import datetime
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.config_loader import ConfigLoader
from src.gmail_client import GmailClient
from src.email_parser import EmailParser
from src.document_classifier import DocumentClassifier
from src.file_manager import FileManager
from src.report_generator import ReportGenerator

console = Console()


@click.command()
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
    help='Comma-separated list of document types to extract (e.g., faturas,contratos)',
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
    '--dry-run',
    is_flag=True,
    help='Run without saving files (for testing)'
)
def main(start_date, end_date, document_types, folder, config_dir, dry_run):
    """Gmail Document Scraper - Intelligent document extraction from Gmail.

    Extracts and classifies documents (invoices, contracts, etc.) from Gmail
    using AI-powered content analysis.

    Examples:

        # Extract all documents from last 30 days
        python main.py --start-date 2024-12-01

        # Extract only invoices from specific period
        python main.py --start-date 2024-01-01 --end-date 2024-12-31 --document-types faturas

        # Dry run to test configuration
        python main.py --start-date 2024-12-01 --dry-run
    """
    console.print("[bold cyan]Gmail Document Scraper v1.0[/bold cyan]\n")

    if dry_run:
        console.print("[yellow]⚠ DRY RUN MODE - No files will be saved[/yellow]\n")

    try:
        # Load configuration
        console.print("[cyan]Loading configuration...[/cyan]")
        config = ConfigLoader(config_dir)
        console.print("[green]✓ Configuration loaded[/green]\n")

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
            console.print("[red]✗ Failed to connect to Gmail. Exiting.[/red]")
            sys.exit(1)

        console.print()

        # Select folder
        if not gmail_client.select_folder(folder):
            console.print(f"[red]✗ Failed to select folder '{folder}'. Exiting.[/red]")
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
            console.print("[yellow]No emails found matching criteria[/yellow]")
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
