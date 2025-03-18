"""Tests for the Guacamole API client module."""

import pytest
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from guacamole_csv_importer.api_client import GuacamoleAPIClient

from responses import matchers
import pytest_responses  # noqa

# Import from conftest.py
from .conftest import (
    BASE_URL,
    handle_request_exception,
    mock_authenticated_response,
    mock_get_connection_groups_response,
    mock_post_connection_create_response,
    mock_post_connection_group,
)


class TestGuacamoleAPIClientInit:
    """Tests for GuacamoleAPIClient.__init__."""

    def test_initialization(self):
        """Test initialization with valid parameters."""
        client = GuacamoleAPIClient(
            base_url=BASE_URL,
            username="admin",
            password="password",
        )
        assert client.base_url == BASE_URL
        assert client.username == "admin"
        assert client.password == "password"
        assert client.token is None

    def test_trailing_slash_removal(self):
        """Test that trailing slashes are removed from the base_url."""
        client = GuacamoleAPIClient(
            base_url=f"{BASE_URL}/",
            username="admin",
            password="password",
        )
        assert client.base_url == BASE_URL


class TestGuacamoleAPIClientAuthenticate:
    """Tests for GuacamoleAPIClient.authenticate."""

    def test_successful_authentication(self, client, api_responses, auth_data):
        mock_authenticated_response(api_responses, auth_data)
        result = client.authenticate()
        assert result is True
        assert client.token == auth_data["token"]

    def test_failed_authentication(self, bad_client, api_responses, auth_data):
        """Test failed authentication."""
        mock_authenticated_response(api_responses, auth_data)
        result = bad_client.authenticate()
        # Verify the token remains None and the method returned False
        assert bad_client.token is None
        assert result is False

    def test_server_error(self, client, api_responses):
        """Test server error during authentication."""
        api_responses.post(f"{BASE_URL}/tokens", body=RequestException("Server error"))

        result = client.authenticate()

        # Verify the token remains None and the method returned False
        assert client.token is None
        assert result is False


class TestGuacamoleAPIClientGetAuthParams:
    """Tests for GuacamoleAPIClient._get_auth_params."""

    def test_valid_token(self, authenticated_client, auth_data):
        """Test _get_auth_params with a valid token."""
        auth_params = authenticated_client._get_auth_params()
        assert auth_params == {"token": auth_data["token"]}

    def test_not_authenticated(self, client):
        """Test _get_auth_params when not authenticated."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client._get_auth_params()


class TestGuacamoleAPIClientGetConnectionGroups:
    """Tests for GuacamoleAPIClient.get_connection_groups."""

    def test_successful_retrieval(self, authenticated_client, api_responses, auth_data):
        """Test successful retrieval of connection groups."""
        mock_get_connection_groups_response(api_responses, auth_data)

        result = authenticated_client.get_connection_groups()

        # Verify the result
        group_ids = result.keys()
        assert len(group_ids) == 2
        assert list(group_ids) == ["1", "2"]
        assert result["1"]["name"] == "group-1"
        assert result["1"]["type"] == "ORGANIZATIONAL"
        assert result["1"]["parentIdentifier"] == "ROOT"

        assert result["2"]["name"] == "group-2"
        assert result["2"]["type"] == "ORGANIZATIONAL"
        assert result["2"]["parentIdentifier"] == "ROOT"

    def test_authentication_failure(self, bad_client, api_responses, auth_data):
        """Test behavior when called without prior authentication."""
        mock_get_connection_groups_response(api_responses, auth_data)
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.get_connection_groups()

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during retrieval."""
        api_responses.get(
            f"{BASE_URL}/session/data/postgresql/connectionGroups",
            body=RequestException("Server error"),
        )

        with pytest.raises(ValueError, match="API request failed: Server error"):
            authenticated_client.get_connection_groups()


class TestGuacamoleAPIClientCreateConnection:
    """Tests for GuacamoleAPIClient.create_connection."""

    def test_successful_creation(
        self, authenticated_client, api_responses, auth_data, connection_data
    ):
        """Test successful creation of a connection."""
        mock_post_connection_create_response(api_responses, auth_data, connection_data)

        result = authenticated_client.create_connection(connection_data)
        assert result == "10"

    def test_invalid_connection_data(self, authenticated_client, api_responses):
        """Test creation with invalid connection data."""
        api_responses.post(
            f"{BASE_URL}/session/data/postgresql/connections",
            json={
                "message": "Connection names must not be blank.",
                "translatableMessage": {
                    "key": "APP.TEXT_UNTRANSLATED",
                    "variables": {"MESSAGE": "Connection names must not be blank."},
                },
                "statusCode": None,
                "expected": None,
                "type": "BAD_REQUEST",
            },
            status=400,
        )

        connection_data = {
            "protocol": "rdp",  # Missing 'name' field
            "parameters": {"hostname": "192.168.1.100", "port": "3389"},
        }

        result = authenticated_client.create_connection(connection_data)

        # Verify the result is None
        assert result is None

    def test_authentication_failure(self, bad_client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.create_connection({"name": "Test"})

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during creation."""
        api_responses.post(
            f"{BASE_URL}/session/data/postgresql/connections",
            body=RequestException("Server error"),
        )

        connection_data = {
            "name": "Test Connection",
            "protocol": "rdp",
            "parameters": {"hostname": "192.168.1.100", "port": "3389"},
        }

        result = authenticated_client.create_connection(connection_data)

        # Verify the result is None
        assert result is None


class TestGuacamoleAPIClientCreateConnectionGroup:
    """Tests for GuacamoleAPIClient.create_connection_group."""

    def test_successful_creation(self, authenticated_client, api_responses, auth_data):
        """Test successful creation of a connection group."""
        mock_post_connection_group(api_responses, auth_data)
        result = authenticated_client.create_connection_group("test-group-1")
        # Verify the result
        assert result == "20"

    def test_invalid_input(self, authenticated_client, api_responses):
        """Test creation with invalid input."""
        api_responses.post(
            f"{BASE_URL}/session/data/postgresql/connectionGroups",
            json={
                "message": "Connection group names must not be blank.",
                "translatableMessage": {
                    "key": "APP.TEXT_UNTRANSLATED",
                    "variables": {
                        "MESSAGE": "Connection group names must not be blank."
                    },
                },
                "statusCode": None,
                "expected": None,
                "type": "BAD_REQUEST",
            },
            status=400,
        )

        result = authenticated_client.create_connection_group(None)

        # Verify the result is None
        assert result is None

    def test_authentication_failure(self, bad_client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.create_connection_group("Test Group")

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during creation."""
        api_responses.post(
            f"{BASE_URL}/session/data/postgresql/connectionGroups",
            body=RequestException("Server error"),
        )

        result = authenticated_client.create_connection_group("Test Group")

        # Verify the result is None
        assert result is None
