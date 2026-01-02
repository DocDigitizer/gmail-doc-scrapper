#!/usr/bin/env python3
"""Quick test script - Process only 10 emails to verify everything works."""

import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader
from src.gmail_client import GmailClient
from src.email_parser import EmailParser
from src.document_classifier import DocumentClassifier

console = Console()

def main():
    """Test with just 10 emails."""

    # Load credentials from environment variables
    import os
    EMAIL = os.getenv('GMAIL_EMAIL')
    APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

    if not EMAIL or not APP_PASSWORD:
        console.print("[red]Error: Gmail credentials not found![/red]")
        console.print("[yellow]Please set environment variables:[/yellow]")
        console.print("  export GMAIL_EMAIL='your-email@gmail.com'")
        console.print("  export GMAIL_APP_PASSWORD='your-app-password'")
        console.print("\nOr create a .env file (see .env.example)")
        return

    console.print("[bold cyan]Quick Test - Processing 10 emails[/bold cyan]\n")

    try:
        # Load config
        config = ConfigLoader("config")
        console.print("[green]✓ Config loaded[/green]")

        # Connect to Gmail
        gmail = GmailClient(EMAIL, APP_PASSWORD)
        if not gmail.connect():
            console.print("[red]✗ Connection failed![/red]")
            console.print("[yellow]Check:[/yellow]")
            console.print("  1. App password is correct (no spaces)")
            console.print("  2. 2FA is enabled")
            console.print("  3. IMAP is enabled in Gmail")
            return

        console.print("[green]✓ Connected to Gmail[/green]\n")

        # Select INBOX
        if not gmail.select_folder("INBOX"):
            console.print("[red]✗ Could not select INBOX[/red]")
            return

        # Search emails from 2025
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)

        console.print(f"[cyan]Searching emails from {start_date.date()} to {end_date.date()}...[/cyan]")
        email_ids = gmail.search_emails(start_date, end_date, has_attachments=True)

        if not email_ids:
            console.print("[yellow]No emails with attachments found![/yellow]")
            return

        console.print(f"[green]✓ Found {len(email_ids)} emails with attachments[/green]")
        console.print(f"[cyan]Processing first 10 emails...[/cyan]\n")

        # Initialize parser and classifier
        parser = EmailParser(config.get('processing.supported_extensions'))
        classifier = DocumentClassifier(config.config, config.rules)

        # Process first 10 emails
        processed = 0
        classified = 0

        for i, email_id in enumerate(email_ids[:10], 1):
            console.print(f"[bold]━━━ Email {i}/10 ━━━[/bold]")

            msg = gmail.fetch_email(email_id)
            if not msg:
                console.print("[yellow]  Could not fetch email[/yellow]\n")
                continue

            processed += 1
            email_data = parser.parse_email(msg)

            console.print(f"  Subject: {email_data['subject'][:60]}...")
            console.print(f"  From: {email_data['from'][:60]}...")
            console.print(f"  Attachments: {len(email_data['attachments'])}")

            if not email_data['attachments']:
                console.print("[dim]  No attachments[/dim]\n")
                continue

            # Process each attachment
            for attachment in email_data['attachments']:
                if attachment.get_extension() != '.pdf':
                    continue

                console.print(f"\n  [cyan]→ {attachment.filename}[/cyan]")

                # Save to temp file and extract text
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(attachment.content)
                    tmp_path = tmp.name

                try:
                    text = classifier.extract_text(tmp_path)

                    if text and len(text) >= 30:
                        result = classifier.classify_document(None, text)
                        if result:
                            classified += 1
                            console.print(f"[green]  ✓ Classified: {result.display_name} ({result.confidence:.0%})[/green]")
                        else:
                            console.print("[yellow]  ✗ Could not classify[/yellow]")
                    else:
                        console.print(f"[yellow]  ✗ Insufficient text: {len(text) if text else 0} chars[/yellow]")

                finally:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

            console.print()

        # Summary
        console.print("\n[bold cyan]═══ Test Summary ═══[/bold cyan]")
        console.print(f"Emails processed: {processed}/10")
        console.print(f"Documents classified: {classified}")

        if classified > 0:
            console.print("\n[bold green]✓ SUCCESS! Classification is working![/bold green]")
            console.print("[cyan]You can now run the full script:[/cyan]")
            console.print("  python main.py --interactive")
        else:
            console.print("\n[bold yellow]⚠ WARNING: No documents classified[/bold yellow]")
            console.print("[yellow]Possible issues:[/yellow]")
            console.print("  1. PDFs are scanned images (need OCR)")
            console.print("  2. PDFs don't match invoice patterns")
            console.print("  3. Classification threshold too high")

        gmail.disconnect()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
