"""Tests for the Guacamole API client module."""

import pytest
from requests.exceptions import RequestException

from guacamole_csv_importer.api_client import GuacamoleAPIClient

import pytest_responses  # noqa

# Import from conftest.py
from .conftest import (
    BASE_URL,
    handle_request_exception,
    mock_authenticated_response,
    mock_get_connection_groups_response,
    mock_get_connections_response,
    mock_post_connection_create_response,
    mock_post_connection_group,
    mock_server_error,
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

    @pytest.mark.parametrize(
        "client_fixture, expected_result, expected_token",
        [
            (
                "client",
                True,
                "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0",
            ),
            ("bad_client", False, None),
        ],
    )
    def test_authentication(
        self,
        client_fixture,
        expected_result,
        expected_token,
        request,
        api_responses,
        auth_data,
    ):
        mock_authenticated_response(api_responses, auth_data)
        client = request.getfixturevalue(client_fixture)
        result = client.authenticate()
        assert result == expected_result
        assert client.token == expected_token

    def test_server_error(self, client, api_responses):
        """Test server error during authentication."""
        mock_server_error(api_responses, f"{BASE_URL}/tokens")

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
        mock_server_error(
            api_responses, f"{BASE_URL}/session/data/postgresql/connectionGroups"
        )

        with pytest.raises(ValueError, match="API request failed: Server error"):
            authenticated_client.get_connection_groups()


class TestGuacamoleAPIClientGetConnections:
    """Tests for GuacamoleAPIClient.get_connections."""

    def test_successful_retrieval(self, authenticated_client, api_responses, auth_data):
        """Test successful retrieval of connection groups."""
        mock_get_connections_response(api_responses, auth_data)

        result = authenticated_client.get_connections()
        print(result)
        # Verify the result
        connection_ids = result.keys()
        assert len(connection_ids) == 2
        assert list(connection_ids) == ["1", "2"]
        assert result["1"]["name"] == "connection-1"
        assert result["1"]["parentIdentifier"] == "ROOT"
        assert result["1"]["protocol"] == "ssh"

        assert result["2"]["name"] == "connection-2"
        assert result["2"]["parentIdentifier"] == "ROOT"
        assert result["2"]["protocol"] == "ssh"

    def test_authentication_failure(self, bad_client, api_responses, auth_data):
        """Test behavior when called without prior authentication."""
        mock_get_connections_response(api_responses, auth_data)
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.get_connections()

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during retrieval."""
        mock_server_error(
            api_responses, f"{BASE_URL}/session/data/postgresql/connections"
        )

        with pytest.raises(ValueError, match="API request failed: Server error"):
            authenticated_client.get_connections()


class TestGuacamoleAPIClientCreateConnection:
    """Tests for GuacamoleAPIClient.create_connection."""

    @pytest.mark.parametrize(
        "connection_data, expected_result, mock_response",
        [
            (
                {  # Valid connection data
                    "name": "Test Connection",
                    "protocol": "ssh",
                    "parameters": {
                        "hostname": "localhost",
                        "port": "22",
                        "username": "guest",
                        "password": "pass",
                    },
                },
                "10",
                lambda api_responses, auth_data, connection_data: mock_post_connection_create_response(
                    api_responses, auth_data, connection_data
                ),
            ),
            (
                {  # Missing 'name' field
                    "protocol": "rdp",
                    "parameters": {"hostname": "192.168.1.100", "port": "3389"},
                },
                None,
                lambda api_responses, auth_data, connection_data: api_responses.post(
                    f"{BASE_URL}/session/data/postgresql/connections",
                    json={
                        "message": "Connection names must not be blank.",
                        "translatableMessage": {
                            "key": "APP.TEXT_UNTRANSLATED",
                            "variables": {
                                "MESSAGE": "Connection names must not be blank."
                            },
                        },
                        "statusCode": None,
                        "expected": None,
                        "type": "BAD_REQUEST",
                    },
                    status=400,
                ),
            ),
        ],
    )
    def test_create_connection(
        self,
        authenticated_client,
        api_responses,
        auth_data,
        connection_data,
        expected_result,
        mock_response,
    ):
        """Test creation of a connection with valid and invalid data."""
        mock_response(api_responses, auth_data, connection_data)
        result = authenticated_client.create_connection(connection_data)
        assert result == expected_result

    def test_authentication_failure(self, bad_client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.create_connection({"name": "Test"})

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during creation."""
        mock_server_error(
            api_responses, f"{BASE_URL}/session/data/postgresql/connections"
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

    @pytest.mark.parametrize(
        "group_name, expected_result, mock_response",
        [
            (
                "test-group-1",
                "20",
                lambda api_responses, auth_data, group_name: mock_post_connection_group(
                    api_responses, auth_data, group_name
                ),
            ),
            (
                None,
                None,
                lambda api_responses, auth_data, group_name: api_responses.post(
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
                ),
            ),
        ],
    )
    def test_create_connection_group(
        self,
        authenticated_client,
        api_responses,
        auth_data,
        group_name,
        expected_result,
        mock_response,
    ):
        """Test creation of a connection group with valid and invalid input."""
        mock_response(api_responses, auth_data, group_name)
        result = authenticated_client.create_connection_group(group_name)
        assert result == expected_result

    def test_authentication_failure(self, bad_client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.create_connection_group("Test Group")

    def test_server_error(self, authenticated_client, api_responses):
        """Test server error during creation."""
        mock_server_error(
            api_responses, f"{BASE_URL}/session/data/postgresql/connectionGroups"
        )

        result = authenticated_client.create_connection_group("Test Group")

        # Verify the result is None
        assert result is None
