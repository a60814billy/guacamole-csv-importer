"""Tests for the Guacamole API client module."""

import pytest
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from guacamole_csv_importer.api_client import GuacamoleAPIClient

from responses import matchers
import pytest_responses  # noqa


@pytest.fixture
def client():
    """Fixture for creating a GuacamoleAPIClient instance."""
    return GuacamoleAPIClient(
        base_url="http://localhost:8080/guacamole/api",
        username="guacadmin",
        password="guacadmin",
    )


@pytest.fixture
def bad_client():
    """Fixture for creating a GuacamoleAPIClient instance."""
    return GuacamoleAPIClient(
        base_url="http://localhost:8080/guacamole/api",
        username="admin",
        password="guacadmin",
    )


MOCK_AUTH_USERNAME = "guacadmin"
MOCK_AUTH_TOKEN = "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0"
MOCK_AUTHENTICATED_RESPONSE = {
    "authToken": MOCK_AUTH_TOKEN,
    "username": MOCK_AUTH_USERNAME,
    "dataSource": "postgresql",
    "availableDataSources": ["postgresql", "postgresql-shared"],
}


@pytest.fixture
def authenticated_client(responses):
    """Fixture for creating an authenticated GuacamoleAPIClient instance."""
    mock_authenticated_response(responses)
    client = GuacamoleAPIClient(
        base_url="http://localhost:8080/guacamole/api",
        username="guacadmin",
        password="guacadmin",
    )
    client.authenticate()
    return client


class TestGuacamoleAPIClientInit:
    """Tests for GuacamoleAPIClient.__init__."""

    def test_initialization(self):
        """Test initialization with valid parameters."""
        client = GuacamoleAPIClient(
            base_url="http://localhost:8080/guacamole/api",
            username="admin",
            password="password",
        )
        assert client.base_url == "http://localhost:8080/guacamole/api"
        assert client.username == "admin"
        assert client.password == "password"
        assert client.token is None

    def test_trailing_slash_removal(self):
        """Test that trailing slashes are removed from the base_url."""
        client = GuacamoleAPIClient(
            base_url="http://localhost:8080/guacamole/api/",
            username="admin",
            password="password",
        )
        assert client.base_url == "http://localhost:8080/guacamole/api"


def mock_get_connection_groups_response(responses):
    responses.get(
        "http://localhost:8080/guacamole/api/session/data/postgresql/connectionGroups",
        json={
            "1": {
                "name": "group-1",
                "identifier": "1",
                "parentIdentifier": "ROOT",
                "type": "ORGANIZATIONAL",
                "activeConnections": 0,
                "attributes": {
                    "max-connections": None,
                    "max-connections-per-user": None,
                    "enable-session-affinity": "",
                },
            },
            "2": {
                "name": "group-2",
                "identifier": "2",
                "parentIdentifier": "ROOT",
                "type": "ORGANIZATIONAL",
                "activeConnections": 0,
                "attributes": {
                    "max-connections": None,
                    "max-connections-per-user": None,
                    "enable-session-affinity": "",
                },
            },
        },
        match=[
            matchers.query_param_matcher({"token": MOCK_AUTH_TOKEN}),
        ],
    )

    responses.get(
        "http://localhost:8080/guacamole/api/session/data/postgresql/connectionGroups",
        json={
            "message": "Permission Denied.",
            "translatableMessage": {
                "key": "APP.TEXT_UNTRANSLATED",
                "variables": {"MESSAGE": "Permission Denied."},
            },
            "statusCode": None,
            "expected": None,
            "type": "PERMISSION_DENIED",
        },
        status=403,
    )


def mock_authenticated_response(responses):
    responses.post(
        "http://localhost:8080/guacamole/api/tokens",
        json=MOCK_AUTHENTICATED_RESPONSE,
        status=200,
        match=[
            matchers.urlencoded_params_matcher(
                {"username": "guacadmin", "password": "guacadmin"}
            )
        ],
    )

    responses.post(
        "http://localhost:8080/guacamole/api/tokens",
        json={
            "message": "Invalid login",
            "translatableMessage": {
                "key": "APP.TEXT_UNTRANSLATED",
                "variables": {"MESSAGE": "Invalid login"},
            },
            "statusCode": None,
            "expected": [
                {"name": "username", "type": "USERNAME"},
                {"name": "password", "type": "PASSWORD"},
            ],
            "type": "INVALID_CREDENTIALS",
        },
        status=403,
        match=[
            matchers.urlencoded_params_matcher(
                {"username": "guacadmin", "password": "guacadmin"}
            )
        ],
    )


class TestGuacamoleAPIClientAuthenticate:
    """Tests for GuacamoleAPIClient.authenticate."""

    def test_successful_authentication(self, client, responses):
        mock_authenticated_response(responses)
        result = client.authenticate()
        assert result is True
        assert client.token == MOCK_AUTH_TOKEN

    def test_failed_authentication(self, bad_client, responses):
        """Test failed authentication."""
        mock_authenticated_response(responses)
        result = bad_client.authenticate()
        # Verify the token remains None and the method returned False
        assert bad_client.token is None
        assert result is False

    def test_server_error(self, client):
        """Test server error during authentication."""
        with patch("requests.Session.post") as mock_post:
            # Mock server error
            mock_post.side_effect = RequestException("Server error")

            result = client.authenticate()

            # Verify the token remains None and the method returned False
            assert client.token is None
            assert result is False


class TestGuacamoleAPIClientGetAuthParams:
    """Tests for GuacamoleAPIClient._get_auth_params."""

    def test_valid_token(self, authenticated_client):
        """Test _get_auth_params with a valid token."""
        auth_params = authenticated_client._get_auth_params()
        assert auth_params == {"token": MOCK_AUTH_TOKEN}

    def test_not_authenticated(self, client):
        """Test _get_auth_params when not authenticated."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client._get_auth_params()


class TestGuacamoleAPIClientGetConnectionGroups:
    """Tests for GuacamoleAPIClient.get_connection_groups."""

    def test_successful_retrieval(self, authenticated_client, responses):
        """Test successful retrieval of connection groups."""
        mock_get_connection_groups_response(responses)

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

    def test_authentication_failure(self, bad_client, responses):
        """Test behavior when called without prior authentication."""
        mock_get_connection_groups_response(responses)
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            bad_client.get_connection_groups()

    def test_server_error(self, authenticated_client):
        """Test server error during retrieval."""
        with patch("requests.Session.get") as mock_get:
            # Mock server error
            mock_get.side_effect = RequestException("Server error")

            with pytest.raises(ValueError, match="API request failed: Server error"):
                authenticated_client.get_connection_groups()


class TestGuacamoleAPIClientCreateConnection:
    """Tests for GuacamoleAPIClient.create_connection."""

    def test_successful_creation(self, authenticated_client):
        """Test successful creation of a connection."""
        with patch("requests.Session.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.text = '"connection-123"'
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            connection_data = {
                "name": "Test Connection",
                "protocol": "rdp",
                "parameters": {"hostname": "192.168.1.100", "port": "3389"},
            }

            result = authenticated_client.create_connection(connection_data)

            # Verify the request was made with correct parameters
            mock_post.assert_called_once_with(
                "http://localhost:8080/guacamole/api/session/data/mysql/connections",
                params={
                    "token": "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0"
                },
                json={
                    "name": "Test Connection",
                    "protocol": "rdp",
                    "parameters": {"hostname": "192.168.1.100", "port": "3389"},
                    "parentIdentifier": "ROOT",
                },
            )

            # Verify the result
            assert result == "connection-123"

    def test_invalid_connection_data(self, authenticated_client):
        """Test creation with invalid connection data."""
        with patch("requests.Session.post") as mock_post:
            # Mock error response
            mock_post.side_effect = RequestException("Invalid connection data")

            connection_data = {
                "protocol": "rdp",  # Missing 'name' field
                "parameters": {"hostname": "192.168.1.100", "port": "3389"},
            }

            result = authenticated_client.create_connection(connection_data)

            # Verify the result is None
            assert result is None

    def test_authentication_failure(self, client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client.create_connection({"name": "Test"})

    def test_server_error(self, authenticated_client):
        """Test server error during creation."""
        with patch("requests.Session.post") as mock_post:
            # Mock server error
            mock_post.side_effect = RequestException("Server error")

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

    def test_successful_creation(self, authenticated_client):
        """Test successful creation of a connection group."""
        with patch("requests.Session.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.text = '"group-123"'
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = authenticated_client.create_connection_group("Test Group")

            # Verify the request was made with correct parameters
            mock_post.assert_called_once_with(
                "http://localhost:8080/guacamole/api/session/data/mysql/connectionGroups",
                params={
                    "token": "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0"
                },
                json={
                    "name": "Test Group",
                    "type": "ORGANIZATIONAL",
                    "parentIdentifier": "ROOT",
                },
            )

            # Verify the result
            assert result == "group-123"

    def test_invalid_input(self, authenticated_client):
        """Test creation with invalid input."""
        with patch("requests.Session.post") as mock_post:
            # Mock error response
            mock_post.side_effect = RequestException("Invalid input")

            result = authenticated_client.create_connection_group("")

            # Verify the result is None
            assert result is None

    def test_authentication_failure(self, client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client.create_connection_group("Test Group")

    def test_server_error(self, authenticated_client):
        """Test server error during creation."""
        with patch("requests.Session.post") as mock_post:
            # Mock server error
            mock_post.side_effect = RequestException("Server error")

            result = authenticated_client.create_connection_group("Test Group")

            # Verify the result is None
            assert result is None
