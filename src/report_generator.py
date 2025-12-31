"""Report generator for scraping operations."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


class ReportGenerator:
    """Generates detailed reports of scraping operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize report generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.report_dir = Path(config['reporting']['report_dir'])
        self.report_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "start_time": datetime.now(),
            "end_time": None,
            "emails_processed": 0,
            "emails_with_attachments": 0,
            "attachments_found": 0,
            "documents_classified": 0,
            "documents_saved": 0,
            "duplicates_skipped": 0,
            "classification_failures": 0,
            "errors": [],
            "by_type": {}
        }

    def record_email_processed(self):
        """Record that an email was processed."""
        self.stats["emails_processed"] += 1

    def record_attachment_found(self, has_attachments: bool = True):
        """Record email with attachments."""
        if has_attachments:
            self.stats["emails_with_attachments"] += 1
        self.stats["attachments_found"] += 1

    def record_classified(self, document_type: str):
        """Record successful classification.

        Args:
            document_type: Type of document classified
        """
        self.stats["documents_classified"] += 1
        self.stats["by_type"][document_type] = \
            self.stats["by_type"].get(document_type, 0) + 1

    def record_saved(self, document_type: str):
        """Record document saved.

        Args:
            document_type: Type of document saved
        """
        self.stats["documents_saved"] += 1

    def record_duplicate(self):
        """Record duplicate skipped."""
        self.stats["duplicates_skipped"] += 1

    def record_classification_failure(self):
        """Record classification failure."""
        self.stats["classification_failures"] += 1

    def record_error(self, error: str):
        """Record an error.

        Args:
            error: Error message
        """
        self.stats["errors"].append({
            "timestamp": datetime.now().isoformat(),
            "error": error
        })

    def finalize(self):
        """Finalize report statistics."""
        self.stats["end_time"] = datetime.now()
        duration = self.stats["end_time"] - self.stats["start_time"]
        self.stats["duration_seconds"] = duration.total_seconds()

    def print_console_report(self):
        """Print report to console."""
        self.finalize()

        # Create summary panel
        duration = self.stats["end_time"] - self.stats["start_time"]

        summary = Text()
        summary.append("Gmail Document Scraper Report\n\n", style="bold cyan")
        summary.append(f"Started:  {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        summary.append(f"Finished: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        summary.append(f"Duration: {duration}\n\n", style="yellow")

        console.print(Panel(summary, title="Summary", border_style="cyan"))

        # Email processing statistics
        email_table = Table(title="Email Processing", show_header=True, header_style="bold magenta")
        email_table.add_column("Metric", style="cyan")
        email_table.add_column("Count", justify="right", style="green")

        email_table.add_row("Emails Processed", str(self.stats["emails_processed"]))
        email_table.add_row("Emails with Attachments", str(self.stats["emails_with_attachments"]))
        email_table.add_row("Total Attachments Found", str(self.stats["attachments_found"]))

        console.print(email_table)
        console.print()

        # Document processing statistics
        doc_table = Table(title="Document Processing", show_header=True, header_style="bold magenta")
        doc_table.add_column("Metric", style="cyan")
        doc_table.add_column("Count", justify="right", style="green")

        doc_table.add_row("Documents Classified", str(self.stats["documents_classified"]))
        doc_table.add_row("Documents Saved", str(self.stats["documents_saved"]))
        doc_table.add_row("Duplicates Skipped", str(self.stats["duplicates_skipped"]))
        doc_table.add_row("Classification Failures", str(self.stats["classification_failures"]))

        console.print(doc_table)
        console.print()

        # Documents by type
        if self.stats["by_type"]:
            type_table = Table(title="Documents by Type", show_header=True, header_style="bold magenta")
            type_table.add_column("Document Type", style="cyan")
            type_table.add_column("Count", justify="right", style="green")

            for doc_type, count in sorted(self.stats["by_type"].items()):
                type_table.add_row(doc_type, str(count))

            console.print(type_table)
            console.print()

        # Errors
        if self.stats["errors"]:
            console.print(f"[red bold]Errors Encountered: {len(self.stats['errors'])}[/red bold]")
            for error in self.stats["errors"][:10]:  # Show first 10 errors
                console.print(f"[red]  • {error['error']}[/red]")
            if len(self.stats["errors"]) > 10:
                console.print(f"[yellow]  ... and {len(self.stats['errors']) - 10} more errors[/yellow]")
            console.print()

        # Success message
        if self.stats["documents_saved"] > 0:
            console.print(
                f"[green bold]Successfully extracted {self.stats['documents_saved']} documents![/green bold]"
            )
            console.print(f"[cyan]Output directory: {self.config['output']['base_dir']}[/cyan]")
        else:
            console.print("[yellow]WARNING: No documents were extracted[/yellow]")

    def save_json_report(self) -> str:
        """Save report to JSON file.

        Returns:
            Path to saved report file
        """
        self.finalize()

        # Generate filename
        timestamp = self.stats["start_time"].strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"report_{timestamp}.json"

        # Convert datetime objects to strings for JSON serialization
        report_data = self.stats.copy()
        report_data["start_time"] = self.stats["start_time"].isoformat()
        report_data["end_time"] = self.stats["end_time"].isoformat()

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            console.print(f"[cyan]Report saved to: {report_file}[/cyan]")
            return str(report_file)
        except Exception as e:
            console.print(f"[red]Failed to save report: {e}[/red]")
            return ""

    def generate_report(self):
        """Generate complete report (console + file)."""
        output_format = self.config['reporting'].get('output_format', 'both')

        if output_format in ['console', 'both']:
            self.print_console_report()

        if output_format in ['file', 'both']:
            self.save_json_report()
