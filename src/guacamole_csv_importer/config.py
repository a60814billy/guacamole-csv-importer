"""Configuration module for Guacamole CSV Importer.

This module handles loading configuration from environment variables or configuration files.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration handler for Guacamole CSV Importer."""

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize the configuration handler.

        Args:
            config_file: Path to a JSON configuration file (optional)
        """
        self.config: Dict[str, Any] = {
            "api_url": os.environ.get("GUACAMOLE_API_URL", ""),
            "username": os.environ.get("GUACAMOLE_USERNAME", ""),
            "password": os.environ.get("GUACAMOLE_PASSWORD", ""),
            "parent_group": os.environ.get("GUACAMOLE_PARENT_GROUP", ""),
        }

        # Load configuration from file if provided
        if config_file:
            self._load_from_file(config_file)

    def _load_from_file(self, config_file: Path) -> None:
        """Load configuration from a JSON file.

        Args:
            config_file: Path to a JSON configuration file
        """
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)

            # Update configuration with values from file
            for key, value in file_config.items():
                if value:  # Only update if value is not empty
                    self.config[key] = value

            logger.info(f"Loaded configuration from {config_file}")

        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration from {config_file}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value to return if key is not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value

    def is_valid(self) -> bool:
        """Check if the configuration is valid.

        Returns:
            True if the configuration is valid, False otherwise
        """
        required_keys = ["api_url", "username", "password"]
        return all(self.config.get(key) for key in required_keys)

    def save_to_file(self, config_file: Path) -> bool:
        """Save the configuration to a JSON file.

        Args:
            config_file: Path to a JSON configuration file

        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        try:
            # Create parent directories if they don't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

            logger.info(f"Saved configuration to {config_file}")
            return True

        except IOError as e:
            logger.error(f"Error saving configuration to {config_file}: {e}")
            return False
