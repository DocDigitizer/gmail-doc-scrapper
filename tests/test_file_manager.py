"""Tests for file manager."""

import pytest
from pathlib import Path
from src.file_manager import FileManager


class TestFileManager:
    """Test cases for FileManager."""

    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration."""
        return {
            "output": {
                "base_dir": str(tmp_path / "output"),
                "structure": "type_and_date",
                "metadata_file": "metadata.json"
            },
            "duplicates": {
                "method": "hash",
                "action": "skip"
            }
        }

    @pytest.fixture
    def file_manager(self, config):
        """Create FileManager instance."""
        return FileManager(config)

    def test_calculate_file_hash(self, file_manager):
        """Test SHA256 hash calculation."""
        content = b"test content"
        hash1 = file_manager.calculate_file_hash(content)
        hash2 = file_manager.calculate_file_hash(content)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64-char hex string

    def test_is_duplicate(self, file_manager):
        """Test duplicate detection."""
        content = b"test content"
        file_hash = file_manager.calculate_file_hash(content)

        # Should not be duplicate initially
        assert not file_manager.is_duplicate(file_hash)

    def test_sanitize_filename(self, file_manager):
        """Test filename sanitization."""
        dangerous_name = "test<>file:name?.pdf"
        safe_name = file_manager._sanitize_filename(dangerous_name)

        # Should not contain invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            assert char not in safe_name

        # Should preserve extension
        assert safe_name.endswith('.pdf')

    def test_get_output_path_type_and_date(self, file_manager):
        """Test output path generation with type_and_date structure."""
        from datetime import datetime

        output_path = file_manager.get_output_path(
            document_type="faturas",
            original_filename="invoice.pdf",
            email_date=datetime(2024, 12, 15)
        )

        # Should follow structure: output/faturas/2024-12/invoice.pdf
        assert "faturas" in str(output_path)
        assert "2024-12" in str(output_path)
        assert output_path.name == "invoice.pdf"


if __name__ == '__main__':
    pytest.main([__file__])
