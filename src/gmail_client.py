"""Gmail IMAP client for email retrieval."""

import imaplib
import email
import time
from email.header import decode_header
from email.message import Message
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
        self.current_folder: Optional[str] = None
        self.last_noop_time: float = 0

    def connect(self) -> bool:
        """Connect to Gmail via IMAP.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            console.print(f"[cyan]Connecting to {self.server}:{self.port}...[/cyan]")
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            self.connection.login(self.email_address, self.password)
            self.last_noop_time = time.time()
            console.print("[green]Connected successfully to Gmail[/green]")
            return True
        except imaplib.IMAP4.error as e:
            console.print(f"[red]IMAP authentication failed: {e}[/red]")
            console.print("[yellow]Make sure you're using an App Password, not your regular password[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]Connection failed: {e}[/red]")
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

    def check_connection(self) -> bool:
        """Check if IMAP connection is still alive.

        Returns:
            True if connection is alive, False otherwise
        """
        if not self.connection:
            return False

        try:
            # NOOP is a harmless command to check connection
            status, _ = self.connection.noop()
            return status == "OK"
        except:
            return False

    def keepalive(self, force: bool = False):
        """Send NOOP command to keep connection alive.

        Gmail IMAP connections timeout after ~30 minutes of inactivity.
        This sends a NOOP every 3 minutes to keep the connection alive.

        Args:
            force: Force sending NOOP even if within interval
        """
        current_time = time.time()

        # Send NOOP every 5 minutes (300 seconds) or if forced - less aggressive to avoid rate limits
        if force or (current_time - self.last_noop_time) >= 300:
            if self.connection:
                try:
                    # Calculate elapsed BEFORE updating last_noop_time
                    elapsed = int(current_time - self.last_noop_time) if hasattr(self, 'last_noop_time') else 0
                    self.connection.noop()
                    self.last_noop_time = current_time
                    console.print(f"[dim]  ♥ Keepalive sent (last: {elapsed//60}m ago)[/dim]")
                except Exception as e:
                    console.print(f"[yellow]  ✗ Keepalive failed: {e}[/yellow]")

    def reconnect(self, max_attempts: int = 10) -> bool:
        """Reconnect to Gmail and reselect current folder.

        Args:
            max_attempts: Maximum number of reconnection attempts (default: 10)

        Returns:
            True if reconnection successful, False otherwise
        """
        console.print("[yellow]Connection lost, attempting to reconnect...[/yellow]")

        # Store current folder
        folder_to_restore = self.current_folder

        for attempt in range(1, max_attempts + 1):
            console.print(f"[cyan]Reconnection attempt {attempt}/{max_attempts}...[/cyan]")

            # Disconnect if still connected
            try:
                if self.connection:
                    self.connection.logout()
            except:
                pass

            self.connection = None

            # Wait before reconnecting (progressive backoff: 5s, 10s, 15s, 20s, 30s...)
            if attempt > 1:
                wait_time = min(5 * attempt, 30)  # 5s, 10s, 15s, 20s, 25s, 30s (max)
                console.print(f"[cyan]Waiting {wait_time}s before retry...[/cyan]")
                time.sleep(wait_time)

            # Reconnect
            if self.connect():
                # Restore folder selection
                if folder_to_restore:
                    if self.select_folder(folder_to_restore):
                        console.print("[green]✓ Reconnected and folder restored successfully[/green]")
                        return True
                    else:
                        console.print(f"[yellow]Could not restore folder '{folder_to_restore}'[/yellow]")
                else:
                    console.print("[green]✓ Reconnected successfully[/green]")
                    return True

        console.print(f"[red]Failed to reconnect after {max_attempts} attempts (total: ~{5*max_attempts//2}s)[/red]")
        return False

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
                self.current_folder = folder  # Save current folder for reconnect
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

    def fetch_email(self, email_id: bytes, verbose: bool = False) -> Optional[Message]:
        """Fetch a single email by ID.

        Args:
            email_id: Email ID to fetch
            verbose: Enable verbose logging for debugging

        Returns:
            Email message object or None
        """
        if not self.connection:
            if verbose:
                console.print(f"[dim red]  Fetch failed: No connection[/dim red]")
            return None

        # Keep connection alive (sends NOOP every 5 minutes)
        self.keepalive()

        # Check if connection is still alive, reconnect if needed
        if not self.check_connection():
            if verbose:
                console.print(f"[dim yellow]  Connection check failed, attempting reconnect...[/dim yellow]")
            if not self.reconnect():
                console.print("[red]Failed to reconnect to Gmail[/red]")
                return None

        try:
            status, msg_data = self.connection.fetch(email_id, "(RFC822)")
        except Exception as e:
            error_str = str(e)
            # Check for rate limiting error
            if "bandwidth" in error_str.lower() or "exceeded" in error_str.lower():
                console.print(f"[yellow]⚠ Gmail rate limit detected! Pausing 60s...[/yellow]")
                time.sleep(60)
                # Try reconnecting
                if self.reconnect():
                    try:
                        status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                    except Exception:
                        if verbose:
                            console.print(f"[dim red]  Fetch retry failed after rate limit[/dim red]")
                        return None
                else:
                    return None
            else:
                if verbose:
                    console.print(f"[dim red]  Fetch exception: {error_str}[/dim red]")
                return None

        try:
            if status != "OK":
                return None

            # Verify msg_data is valid before accessing
            if not msg_data or len(msg_data) == 0:
                return None

            # msg_data is a list of tuples: [(b'1 (RFC822 {size}', b'email content'), b')']
            # We need the email content which is in msg_data[0][1]
            if not isinstance(msg_data[0], tuple) or len(msg_data[0]) < 2:
                return None

            email_body = msg_data[0][1]
            
            if not email_body:
                return None

            # Parse email
            return email.message_from_bytes(email_body)
        except (IndexError, TypeError) as e:
            # Silently skip emails that can't be fetched (deleted, moved, etc.)
            return None
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

    def get_email_metadata(self, msg: Message) -> Dict[str, Any]:
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

    def list_folders(self) -> List[str]:
        """List all available IMAP folders.

        Returns:
            List of folder names
        """
        if not self.connection:
            console.print("[red]Not connected to Gmail[/red]")
            return []

        try:
            status, folders = self.connection.list()
            if status != "OK":
                return []

            folder_list = []
            for folder_data in folders:
                # Parse folder name from IMAP response
                # Format: (\HasNoChildren) "/" "FolderName"
                folder_str = folder_data.decode() if isinstance(folder_data, bytes) else str(folder_data)
                
                # Extract folder name (last quoted part)
                import re
                match = re.search(r'"([^"]+)"\s*$', folder_str)
                if match:
                    folder_name = match.group(1)
                    folder_list.append(folder_name)

            return folder_list
        except Exception as e:
            console.print(f"[yellow]Failed to list folders: {e}[/yellow]")
            return []

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
