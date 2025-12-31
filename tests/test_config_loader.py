"""Tests for configuration loader."""

import pytest
import tempfile
import yaml
from pathlib import Path
from src.config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader."""

    def test_load_yaml_success(self, tmp_path):
        """Test loading valid YAML file."""
        # Create test config
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        test_config = {
            "imap": {
                "server": "imap.test.com",
                "port": 993
            }
        }

        config_file = config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)

        # Create rules file
        rules_file = config_dir / "rules.yaml"
        with open(rules_file, 'w') as f:
            yaml.dump({"test": {}}, f)

        # Create .env file in project root
        env_file = tmp_path / ".env"
        with open(env_file, 'w') as f:
            f.write("GMAIL_EMAIL=test@test.com\n")
            f.write("GMAIL_APP_PASSWORD=testpassword\n")

        # This test would need proper env setup
        # In real tests, use pytest fixtures and environment manipulation

    def test_get_document_types(self):
        """Test getting configured document types."""
        # Would need proper fixture setup
        pass

    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        # Would need proper fixture setup
        pass


if __name__ == '__main__':
    pytest.main([__file__])
