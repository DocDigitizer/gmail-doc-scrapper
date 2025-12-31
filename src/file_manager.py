"""File manager for organizing and deduplicating documents."""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from rich.console import Console

console = Console()


@dataclass
class FileMetadata:
    """Metadata for a processed file."""
    filename: str
    original_filename: str
    document_type: str
    classification_confidence: float
    file_hash: str
    file_size: int
    email_subject: str
    email_from: str
    email_date: str
    extraction_date: str
    output_path: str


class FileManager:
    """Manages file organization and duplicate detection."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize file manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_dir = Path(config['output']['base_dir'])
        self.structure = config['output']['structure']
        self.metadata_file = self.output_dir / config['output']['metadata_file']

        # Load existing metadata
        self.metadata: Dict[str, FileMetadata] = {}
        self.file_hashes: Dict[str, str] = {}  # hash -> filepath
        self._load_metadata()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self):
        """Load existing metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    file_meta = FileMetadata(**item)
                    self.metadata[file_meta.output_path] = file_meta
                    self.file_hashes[file_meta.file_hash] = file_meta.output_path

                console.print(f"[cyan]Loaded {len(self.metadata)} existing file records[/cyan]")
            except Exception as e:
                console.print(f"[yellow]Failed to load metadata: {e}[/yellow]")

    def _save_metadata(self):
        """Save metadata to disk."""
        try:
            data = [asdict(meta) for meta in self.metadata.values()]

            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            console.print(f"[red]Failed to save metadata: {e}[/red]")

    def calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA256 hash of file content.

        Args:
            content: File content as bytes

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()

    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file is a duplicate.

        Args:
            file_hash: SHA256 hash of file

        Returns:
            True if duplicate exists, False otherwise
        """
        return file_hash in self.file_hashes

    def get_output_path(self, document_type: str, original_filename: str,
                       email_date: Optional[datetime] = None) -> Path:
        """Generate output path for a document.

        Args:
            document_type: Type of document (e.g., 'faturas')
            original_filename: Original file name
            email_date: Date from email (optional)

        Returns:
            Path object for output location
        """
        # Clean filename
        filename = self._sanitize_filename(original_filename)

        if self.structure == "type_and_date":
            # output/faturas/2025-01/document.pdf
            if email_date:
                year_month = email_date.strftime("%Y-%m")
            else:
                year_month = datetime.now().strftime("%Y-%m")

            output_path = self.output_dir / document_type / year_month / filename

        elif self.structure == "date_only":
            # output/2025-01/document.pdf
            if email_date:
                year_month = email_date.strftime("%Y-%m")
            else:
                year_month = datetime.now().strftime("%Y-%m")

            # Prefix filename with type
            filename = f"{document_type}_{filename}"
            output_path = self.output_dir / year_month / filename

        else:  # flat
            # output/document.pdf
            filename = f"{document_type}_{filename}"
            output_path = self.output_dir / filename

        return output_path

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        name = Path(filename).stem[:200]
        ext = Path(filename).suffix
        return f"{name}{ext}"

    def save_file(self, content: bytes, document_type: str,
                  original_filename: str, email_metadata: Dict[str, Any],
                  classification_confidence: float) -> Optional[str]:
        """Save file to disk with metadata tracking.

        Args:
            content: File content
            document_type: Classified document type
            original_filename: Original filename from email
            email_metadata: Email metadata dictionary
            classification_confidence: Classification confidence score

        Returns:
            Output file path if successful, None if duplicate or error
        """
        # Calculate hash
        file_hash = self.calculate_file_hash(content)

        # Check for duplicates
        if self.is_duplicate(file_hash):
            existing_path = self.file_hashes[file_hash]
            console.print(f"[yellow]⊗ Duplicate detected: {original_filename}[/yellow]")
            console.print(f"[yellow]  Existing file: {existing_path}[/yellow]")
            return None

        # Get output path
        email_date = email_metadata.get('date')
        output_path = self.get_output_path(document_type, original_filename, email_date)

        # Handle existing file with same name (but different content)
        if output_path.exists():
            output_path = self._get_unique_path(output_path)

        # Create directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        try:
            with open(output_path, 'wb') as f:
                f.write(content)

            # Create metadata record
            file_meta = FileMetadata(
                filename=output_path.name,
                original_filename=original_filename,
                document_type=document_type,
                classification_confidence=classification_confidence,
                file_hash=file_hash,
                file_size=len(content),
                email_subject=email_metadata.get('subject', ''),
                email_from=email_metadata.get('from', ''),
                email_date=str(email_metadata.get('date', '')),
                extraction_date=datetime.now().isoformat(),
                output_path=str(output_path.relative_to(self.output_dir))
            )

            # Update tracking
            self.metadata[str(output_path.relative_to(self.output_dir))] = file_meta
            self.file_hashes[file_hash] = str(output_path.relative_to(self.output_dir))

            # Save metadata
            self._save_metadata()

            console.print(f"[green]✓ Saved: {output_path.relative_to(self.output_dir)}[/green]")
            return str(output_path)

        except Exception as e:
            console.print(f"[red]Failed to save {original_filename}: {e}[/red]")
            return None

    def _get_unique_path(self, path: Path) -> Path:
        """Get unique path by adding suffix if file exists.

        Args:
            path: Original path

        Returns:
            Unique path
        """
        if not path.exists():
            return path

        counter = 1
        while True:
            new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed files.

        Returns:
            Dictionary with statistics
        """
        if not self.metadata:
            return {
                "total_files": 0,
                "by_type": {},
                "total_size_mb": 0.0
            }

        # Count by type
        by_type = {}
        total_size = 0

        for meta in self.metadata.values():
            doc_type = meta.document_type
            by_type[doc_type] = by_type.get(doc_type, 0) + 1
            total_size += meta.file_size

        return {
            "total_files": len(self.metadata),
            "by_type": by_type,
            "total_size_mb": total_size / (1024 * 1024)
        }

    def get_files_by_type(self, document_type: str) -> List[FileMetadata]:
        """Get all files of a specific type.

        Args:
            document_type: Document type to filter

        Returns:
            List of FileMetadata objects
        """
        return [
            meta for meta in self.metadata.values()
            if meta.document_type == document_type
        ]
