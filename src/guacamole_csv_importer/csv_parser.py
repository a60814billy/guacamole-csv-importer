"""CSV parsing module for Guacamole connection imports.

This module handles the parsing and validation of CSV files containing
Guacamole connection information.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CSVParser:
    """Parser for CSV files containing Guacamole connection information."""

    def __init__(self, file_path: str):
        """Initialize the CSV parser.

        Args:
            file_path: Path to the CSV file to parse
        """
        self.file_path = Path(file_path)
        # site,device_name,hostname,protocol,port,username,password
        self.required_fields = [
            "site",
            "device_name",
            "hostname",
            "protocol",
            "port",
            "username",
            "password",
        ]

    def validate_headers(self, headers: List[str]) -> bool:
        """Validate that the CSV file contains the required headers.

        Args:
            headers: List of headers from the CSV file

        Returns:
            True if all required fields are present, False otherwise
        """
        missing_fields = [
            field for field in self.required_fields if field not in headers
        ]
        if missing_fields:
            logger.error(f"Missing required fields in CSV: {', '.join(missing_fields)}")
            return False
        return True

    def parse(self) -> List[Dict[str, Any]]:
        """Parse the CSV file and return a list of connection dictionaries.

        Returns:
            List of dictionaries, each representing a connection

        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file is invalid
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        connections = []

        try:
            with open(self.file_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate headers
                if reader.fieldnames is None:
                    raise ValueError("Invalid CSV file")
                if not self.validate_headers(list(reader.fieldnames)):
                    raise ValueError("Invalid CSV headers")

                # Parse connections
                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 to account for header row
                    try:
                        connection = self._process_row(row)
                        if connection:
                            connections.append(connection)
                    except ValueError as e:
                        logger.warning(f"Skipping row {row_num}: {e}")

        except csv.Error as e:
            raise ValueError(f"Error parsing CSV file: {e}")

        logger.info(f"Successfully parsed {len(connections)} connections from CSV")
        return connections

    def _process_row(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process a single row from the CSV file.

        Args:
            row: Dictionary representing a row from the CSV file

        Returns:
            Processed connection dictionary or None if the row should be skipped

        Raises:
            ValueError: If the row is invalid
        """
        # Check for empty required fields
        for field in self.required_fields:
            if not row.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Process the connection data
        connection: Dict[str, Any] = {
            "site": row["site"],
            "device_name": row["device_name"],
            "protocol": row["protocol"],
            "hostname": row["hostname"],
            "port": row["port"],
            "username": row["username"],
            "password": row["password"],
        }

        # Add optional parameters if present
        for key, value in row.items():
            if (
                key not in self.required_fields
                and key not in ["name", "protocol"]
                and value
            ):
                connection["parameters"][key] = value

        return connection
