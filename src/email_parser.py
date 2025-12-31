"""Email parser for extracting attachments and content."""

import email
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from email.message import Message
from rich.console import Console

console = Console()


class EmailAttachment:
    """Represents an email attachment."""

    def __init__(self, filename: str, content: bytes, content_type: str):
        """Initialize attachment.

        Args:
            filename: Original filename
            content: File content as bytes
            content_type: MIME content type
        """
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self.size = len(content)

    def get_extension(self) -> str:
        """Get file extension.

        Returns:
            File extension including dot (e.g., '.pdf')
        """
        return Path(self.filename).suffix.lower()

    def save(self, output_path: str) -> bool:
        """Save attachment to disk.

        Args:
            output_path: Path where to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(self.content)

            return True
        except Exception as e:
            console.print(f"[red]Failed to save {self.filename}: {e}[/red]")
            return False


class EmailParser:
    """Parser for extracting data from email messages."""

    def __init__(self, supported_extensions: List[str]):
        """Initialize email parser.

        Args:
            supported_extensions: List of supported file extensions
        """
        self.supported_extensions = [ext.lower() for ext in supported_extensions]

    def parse_email(self, msg: Message) -> Dict[str, Any]:
        """Parse email message and extract data.

        Args:
            msg: Email message object

        Returns:
            Dictionary with parsed email data
        """
        result = {
            "subject": self._decode_header(msg.get("Subject", "")),
            "from": self._decode_header(msg.get("From", "")),
            "to": self._decode_header(msg.get("To", "")),
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "body": self._extract_body(msg),
            "attachments": self._extract_attachments(msg)
        }

        return result

    def _decode_header(self, header_value: str) -> str:
        """Decode email header value.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return ""

        from email.header import decode_header

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += str(part)

        return decoded_string

    def _extract_body(self, msg: Message) -> str:
        """Extract email body text.

        Args:
            msg: Email message object

        Returns:
            Email body as string
        """
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in disposition:
                    continue

                # Extract text content
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    # Fallback to HTML if no plain text
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_body = payload.decode('utf-8', errors='ignore')
                            # Basic HTML stripping (for simple cases)
                            import re
                            body = re.sub('<[^<]+?>', '', html_body)
                    except:
                        pass
        else:
            # Not multipart
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except:
                pass

        return body.strip()

    def _extract_attachments(self, msg: Message) -> List[EmailAttachment]:
        """Extract attachments from email.

        Args:
            msg: Email message object

        Returns:
            List of EmailAttachment objects
        """
        attachments = []

        for part in msg.walk():
            # Check if part is an attachment
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if not filename:
                continue

            # Decode filename
            filename = self._decode_header(filename)

            # Check if extension is supported
            extension = Path(filename).suffix.lower()
            if extension not in self.supported_extensions:
                console.print(f"[yellow]Skipping unsupported file: {filename}[/yellow]")
                continue

            # Extract content
            try:
                content = part.get_payload(decode=True)
                if content:
                    content_type = part.get_content_type()
                    attachment = EmailAttachment(filename, content, content_type)
                    attachments.append(attachment)
                    console.print(f"[green]✓ Extracted: {filename} ({attachment.size} bytes)[/green]")
            except Exception as e:
                console.print(f"[red]Failed to extract {filename}: {e}[/red]")

        return attachments

    def filter_attachments_by_size(self, attachments: List[EmailAttachment],
                                   max_size_mb: float) -> List[EmailAttachment]:
        """Filter attachments by maximum size.

        Args:
            attachments: List of attachments
            max_size_mb: Maximum size in megabytes

        Returns:
            Filtered list of attachments
        """
        max_bytes = max_size_mb * 1024 * 1024
        filtered = []

        for att in attachments:
            if att.size <= max_bytes:
                filtered.append(att)
            else:
                size_mb = att.size / (1024 * 1024)
                console.print(
                    f"[yellow]Skipping {att.filename}: "
                    f"size {size_mb:.2f}MB exceeds limit {max_size_mb}MB[/yellow]"
                )

        return filtered
