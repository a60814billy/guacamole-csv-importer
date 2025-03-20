"""Guacamole CSV Importer module.

This module provides the main functionality for importing connections from CSV files
into Apache Guacamole.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import time

from .csv_parser import CSVParser
from .connection_csv_data import ConnectionCsvData
from .api_client import GuacamoleAPIClient
from .connection_group_tree import (
    ConnectionGroupTree,
    ConnectionGroupNode,
    ConnectionNode,
)

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

        existing_connection_groups = self.api_client.get_connection_groups()
        logger.info(f"Existing connection groups: {existing_connection_groups}")
        existing_connections = self.api_client.get_connections()
        logger.info(f"Existing connections: {existing_connections}")

        tree = ConnectionGroupTree()
        tree.build_from_data(existing_connection_groups, existing_connections)

        connections = self.csv_parser.parse()
        connection_data: List[ConnectionCsvData] = []
        for connection in connections:
            conn_data = ConnectionCsvData.from_dict(connection)
            connection_data.append(conn_data)

        for connection in connection_data:
            parent_grp = tree.path_mapping.get(connection.site)

            if parent_grp is None:
                # create the group
                sep_path = connection.site.split("/")
                if sep_path[0] != "ROOT":
                    sep_path.insert(0, "ROOT")

                node: ConnectionGroupNode = tree.path_mapping.get("ROOT")
                for i in range(1, len(sep_path)):
                    path_name = sep_path[i]
                    grp = node.get_group_in_children(path_name)
                    if grp is None:
                        group_id = self.api_client.create_connection_group(
                            name=path_name, parentIdentifier=node.identifier
                        )
                        # need to build the group
                        grp = node.add_group(
                            {
                                "name": path_name,
                                "identifier": group_id,
                                "parentIdentifier": node.identifier,
                                "type": "ORGANIZATIONAL",
                                "activeConnections": 0,
                                "attributes": {},
                            }
                        )
                        # need refactor
                        tree.path_mapping[tree.reverse_get_full_path_name(grp)] = grp
                    node = grp

                parent_grp = node

            # check connection in the grp
            conn = parent_grp.get_connection_in_children(connection.device_name)
            if conn is None:
                # create connection in the group
                conn_resp = self.api_client.create_connection(
                    connection.to_dict(), parent_grp.identifier
                )
                parent_grp.add_connection(
                    {
                        "name": connection.device_name,
                        "identifier": conn_resp,
                        "parentIdentifier": parent_grp.identifier,
                        "protocol": connection.protocol,
                        "attributes": {
                            "guacd-encryption": "none",
                            "failover-only": "true",
                            "weight": None,
                            "max-connections": "15",
                            "guacd-hostname": "guacd",
                            "guacd-port": "4822",
                            "max-connections-per-user": "1",
                        },
                    }
                )

        tree.print_tree()
        return
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
