"""Configuration loader for the Gmail document scraper."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigLoader:
    """Loads and manages application configuration."""

    def __init__(self, config_dir: str = "config"):
        """Initialize the config loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        load_dotenv()

        self.config = self._load_yaml("config.yaml")
        self.rules = self._load_yaml("rules.yaml")
        self._merge_env_vars()

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file.

        Args:
            filename: Name of the YAML file

        Returns:
            Parsed configuration dictionary
        """
        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _merge_env_vars(self):
        """Merge environment variables into configuration."""
        # Gmail credentials
        self.gmail_email = os.getenv("GMAIL_EMAIL")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")

        if not self.gmail_email or not self.gmail_password:
            raise ValueError(
                "GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in .env file"
            )

        # IMAP settings from env (with fallbacks to config)
        self.config['imap']['server'] = os.getenv(
            "IMAP_SERVER",
            self.config['imap']['server']
        )
        self.config['imap']['port'] = int(os.getenv(
            "IMAP_PORT",
            self.config['imap']['port']
        ))

        # Output directory
        output_dir = os.getenv("OUTPUT_DIR", self.config['output']['base_dir'])
        self.config['output']['base_dir'] = output_dir

        # OCR settings
        enable_ocr = os.getenv("ENABLE_OCR", "true").lower() == "true"
        self.config['processing']['enable_ocr'] = enable_ocr

        # Confidence threshold
        threshold = float(os.getenv(
            "CONFIDENCE_THRESHOLD",
            self.config['classification']['confidence_threshold']
        ))
        self.config['classification']['confidence_threshold'] = threshold

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'imap.server')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_document_types(self) -> list:
        """Get list of configured document types.

        Returns:
            List of document type names
        """
        return list(self.rules.keys())

    def get_rule(self, doc_type: str) -> Dict[str, Any]:
        """Get classification rule for a document type.

        Args:
            doc_type: Document type name

        Returns:
            Rule configuration dictionary
        """
        return self.rules.get(doc_type, {})
