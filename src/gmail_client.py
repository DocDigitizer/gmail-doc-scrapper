"""Gmail IMAP client for email retrieval."""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class GmailClient:
    """IMAP client for connecting to Gmail and retrieving emails."""

    def __init__(self, email_address: str, password: str,
                 server: str = "imap.gmail.com", port: int = 993):
        """Initialize Gmail client.

        Args:
            email_address: Gmail email address
            password: Gmail app password
            server: IMAP server address
            port: IMAP server port
        """
        self.email_address = email_address
        self.password = password
        self.server = server
        self.port = port
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Connect to Gmail via IMAP.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            console.print(f"[cyan]Connecting to {self.server}:{self.port}...[/cyan]")
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            self.connection.login(self.email_address, self.password)
            console.print("[green]✓ Connected successfully to Gmail[/green]")
            return True
        except imaplib.IMAP4.error as e:
            console.print(f"[red]✗ IMAP authentication failed: {e}[/red]")
            console.print("[yellow]Make sure you're using an App Password, not your regular password[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            return False

    def disconnect(self):
        """Disconnect from Gmail."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                console.print("[cyan]Disconnected from Gmail[/cyan]")
            except:
                pass

    def select_folder(self, folder: str = "INBOX") -> bool:
        """Select an IMAP folder.

        Args:
            folder: Folder name to select

        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            console.print("[red]Not connected to Gmail[/red]")
            return False

        try:
            status, messages = self.connection.select(folder)
            if status == "OK":
                num_messages = int(messages[0])
                console.print(f"[cyan]Selected folder '{folder}' ({num_messages} messages)[/cyan]")
                return True
            return False
        except Exception as e:
            console.print(f"[red]Failed to select folder '{folder}': {e}[/red]")
            return False

    def search_emails(self, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     has_attachments: bool = True) -> List[bytes]:
        """Search for emails within date range.

        Args:
            start_date: Start date for search (inclusive)
            end_date: End date for search (inclusive)
            has_attachments: Only return emails with attachments

        Returns:
            List of email IDs
        """
        if not self.connection:
            console.print("[red]Not connected to Gmail[/red]")
            return []

        # Build search criteria
        criteria = []

        if start_date:
            date_str = start_date.strftime("%d-%b-%Y")
            criteria.append(f'SINCE {date_str}')

        if end_date:
            date_str = end_date.strftime("%d-%b-%Y")
            criteria.append(f'BEFORE {date_str}')

        # Search for emails
        search_string = " ".join(criteria) if criteria else "ALL"

        try:
            console.print(f"[cyan]Searching emails with criteria: {search_string}[/cyan]")
            status, messages = self.connection.search(None, search_string)

            if status != "OK":
                console.print("[red]Email search failed[/red]")
                return []

            email_ids = messages[0].split()
            console.print(f"[green]Found {len(email_ids)} emails[/green]")

            return email_ids
        except Exception as e:
            console.print(f"[red]Search failed: {e}[/red]")
            return []

    def fetch_email(self, email_id: bytes) -> Optional[email.message.Message]:
        """Fetch a single email by ID.

        Args:
            email_id: Email ID to fetch

        Returns:
            Email message object or None
        """
        if not self.connection:
            return None

        try:
            status, msg_data = self.connection.fetch(email_id, "(RFC822)")

            if status != "OK":
                return None

            # Parse email
            email_body = msg_data[0][1]
            return email.message_from_bytes(email_body)
        except Exception as e:
            console.print(f"[yellow]Failed to fetch email {email_id}: {e}[/yellow]")
            return None

    def decode_header_value(self, header_value: str) -> str:
        """Decode email header value.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += part

        return decoded_string

    def get_email_metadata(self, msg: email.message.Message) -> Dict[str, Any]:
        """Extract metadata from email message.

        Args:
            msg: Email message object

        Returns:
            Dictionary with email metadata
        """
        subject = self.decode_header_value(msg.get("Subject", ""))
        from_addr = self.decode_header_value(msg.get("From", ""))
        date_str = msg.get("Date", "")

        # Parse date
        email_date = None
        try:
            email_date = email.utils.parsedate_to_datetime(date_str)
        except:
            pass

        return {
            "subject": subject,
            "from": from_addr,
            "date": email_date,
            "message_id": msg.get("Message-ID", ""),
            "has_attachments": any(part.get_filename() for part in msg.walk())
        }

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
