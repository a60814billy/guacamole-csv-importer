"""Guacamole CSV Importer module.

This module provides the main functionality for importing connections from CSV files
into Apache Guacamole.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time

from .csv_parser import CSVParser
from .api_client import GuacamoleAPIClient

logger = logging.getLogger(__name__)


class ConnectionImporter:
    """Importer for Guacamole connections from CSV files."""

    def __init__(self, api_client: GuacamoleAPIClient):
        """Initialize the connection importer.

        Args:
            api_client: Guacamole API client
        """
        self.api_client = api_client

    def import_connections(self, csv_file_path: str) -> Tuple[int, int]:
        """Import connections from the CSV file into Guacamole.

        Returns:
            Tuple of (number of successful imports, total number of connections)

        Raises:
            ValueError: If authentication fails or CSV parsing fails
        """

        self.csv_parser = CSVParser(csv_file_path)

        # Authenticate with the Guacamole API
        if not self.api_client.authenticate():
            raise ValueError("Failed to authenticate with Guacamole API")

        # Parse the CSV file
        connections = self.csv_parser.parse()
        total_connections = len(connections)

        if total_connections == 0:
            logger.warning("No connections found in CSV file")
            return 0, 0

        # Create parent group if specified
        parent_id = "ROOT"
        if self.parent_group:
            parent_id = self.api_client.create_connection_group(self.parent_group)
            if not parent_id:
                logger.warning(
                    f"Failed to create parent group '{self.parent_group}', using ROOT"
                )
                parent_id = "ROOT"

        # Import connections
        successful_imports = 0
        for connection in connections:
            if self._import_connection(connection, parent_id):
                successful_imports += 1

            # Small delay to avoid overwhelming the API
            time.sleep(0.1)

        logger.info(
            f"Imported {successful_imports}/{total_connections} connections successfully"
        )
        return successful_imports, total_connections

    def _import_connection(self, connection: Dict[str, Any], parent_id: str) -> bool:
        """Import a single connection into Guacamole.

        Args:
            connection: Connection data dictionary
            parent_id: ID of the parent connection group

        Returns:
            True if the connection was imported successfully, False otherwise
        """
        connection_name = connection.get("name", "Unknown")

        try:
            # Format connection data for Guacamole API
            api_connection = {
                "name": connection["name"],
                "protocol": connection["protocol"],
                "parameters": connection["parameters"],
            }

            # Create the connection
            connection_id = self.api_client.create_connection(api_connection, parent_id)

            if connection_id:
                logger.info(f"Successfully imported connection '{connection_name}'")
                return True
            else:
                logger.error(f"Failed to import connection '{connection_name}'")
                return False

        except KeyError as e:
            logger.error(
                f"Missing required field in connection '{connection_name}': {e}"
            )
            return False
        except Exception as e:
            logger.error(f"Error importing connection '{connection_name}': {e}")
            return False
