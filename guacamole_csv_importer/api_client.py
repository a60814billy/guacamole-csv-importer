"""Guacamole API client module.

This module provides a client for interacting with the Guacamole REST API.
"""

import logging
import json
from typing import Dict, List, Any, Optional
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class GuacamoleAPIClient:
    """Client for interacting with the Guacamole REST API."""

    def __init__(self, base_url: str, username: str, password: str):
        """Initialize the Guacamole API client.

        Args:
            base_url: Base URL of the Guacamole API (e.g., 'http://localhost:8080/guacamole/api')
            username: Guacamole admin username
            password: Guacamole admin password
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = None
        self.data_source = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate with the Guacamole API.

        Returns:
            True if authentication was successful, False otherwise
        """
        auth_url = f"{self.base_url}/tokens"

        try:
            response = self.session.post(
                auth_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"username": self.username, "password": self.password},
            )
            response.raise_for_status()

            data = response.json()
            if "authToken" in data:
                self.token = data["authToken"]
                self.data_source = data["dataSource"]
                logger.info("Successfully authenticated with Guacamole API")
                logger.debug(f"Data source: {self.data_source}")
                return True

        except RequestException as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters for API requests.

        Returns:
            Dictionary of authentication parameters
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        return {"token": self.token}

    def get_connection_groups(self) -> List[Dict[str, Any]]:
        """Get all connection groups.

        Returns:
            List of connection group dictionaries

        Raises:
            ValueError: If not authenticated or API request fails
        """
        url = f"{self.base_url}/session/data/{self.data_source}/connectionGroups"

        try:
            response = self.session.get(url, params=self._get_auth_params())
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get connection groups: {e}")
            raise ValueError(f"API request failed: {e}")

    def get_connections(self) -> List[Dict[str, Any]]:
        """Get all connections.

        Returns:
            List of connection dictionaries

        Raises:
            ValueError: If not authenticated or API request fails
        """
        url = f"{self.base_url}/session/data/{self.data_source}/connections"

        try:
            response = self.session.get(url, params=self._get_auth_params())
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to get connections: {e}")
            raise ValueError(f"API request failed: {e}")

    def create_connection(
        self, connection_data: Dict[str, Any], parent_id: str = "ROOT"
    ) -> Optional[str]:
        """Create a new connection.

        Args:
            connection_data: Connection data dictionary
            parent_id: ID of the parent connection group (default: "ROOT")

        Returns:
            ID of the created connection if successful, None otherwise
        """
        url = f"{self.base_url}/session/data/{self.data_source}/connections"

        # Add parent identifier
        connection_data["parentIdentifier"] = parent_id

        connection_data["attributes"] = {
            "guacd-hostname": "guacd",
            "guacd-port": "4822",
            "guacd-encryption": "none",
        }

        try:
            response = self.session.post(
                url,
                params=self._get_auth_params(),
                json=connection_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            # Extract connection ID from response
            connection_id = response.json().get("identifier")
            logger.info(
                f"Created connection '{connection_data.get('name')}' with ID {connection_id}"
            )
            return connection_id

        except RequestException as e:
            logger.error(
                f"Failed to create connection '{connection_data.get('name')}': {e}"
            )
            return None

    def create_connection_group(
        self, name: str, parent_id: str = "ROOT"
    ) -> Optional[str]:
        """Create a new connection group.

        Args:
            name: Name of the connection group
            parent_id: ID of the parent connection group (default: "ROOT")

        Returns:
            ID of the created connection group if successful, None otherwise
        """
        url = f"{self.base_url}/session/data/{self.data_source}/connectionGroups"

        group_data = {
            "parentIdentifier": parent_id,
            "name": name,
            "type": "ORGANIZATIONAL",
            "attributes": {
                "max-connections": "",
                "max-connections-per-user": "",
                "enable-session-affinity": "",
            },
        }

        try:
            response = self.session.post(
                url, params=self._get_auth_params(), json=group_data
            )
            response.raise_for_status()

            # Extract group ID from response
            group_id = response.json().get("identifier")
            logger.info(f"Created connection group '{name}' with ID {group_id}")
            return group_id

        except RequestException as e:
            logger.error(f"Failed to create connection group '{name}': {e}")
            return None
