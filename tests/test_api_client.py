"""Tests for the Guacamole API client module."""

import pytest
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from guacamole_csv_importer.api_client import GuacamoleAPIClient


@pytest.fixture
def client():
    """Fixture for creating a GuacamoleAPIClient instance."""
    return GuacamoleAPIClient(
        base_url="http://localhost:8080/guacamole/api",
        username="admin",
        password="password",
    )


@pytest.fixture
def authenticated_client():
    """Fixture for creating an authenticated GuacamoleAPIClient instance."""
    with patch("requests.Session.post") as mock_post:
        # Mock successful authentication response
        mock_response = Mock()
        mock_response.json.return_value = {"authToken": "mock-token"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = GuacamoleAPIClient(
            base_url="http://localhost:8080/guacamole/api",
            username="admin",
            password="password",
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


class TestGuacamoleAPIClientAuthenticate:
    """Tests for GuacamoleAPIClient.authenticate."""

    def test_successful_authentication(self, client):
        """Test successful authentication."""
        with patch("requests.Session.post") as mock_post:
            # Mock successful authentication response
            mock_response = Mock()
            mock_response.json.return_value = {"authToken": "mock-token"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = client.authenticate()

            # Verify the request was made with correct parameters
            mock_post.assert_called_once_with(
                "http://localhost:8080/guacamole/api/tokens",
                params={"username": "admin", "password": "password"},
            )

            # Verify the token was set and the method returned True
            assert client.token == "mock-token"
            assert result is True

    def test_failed_authentication(self, client):
        """Test failed authentication."""
        with patch("requests.Session.post") as mock_post:
            # Mock failed authentication response
            mock_response = Mock()
            mock_response.json.return_value = {"error": "Invalid credentials"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = client.authenticate()

            # Verify the token remains None and the method returned False
            assert client.token is None
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
        assert auth_params == {"token": "mock-token"}

    def test_not_authenticated(self, client):
        """Test _get_auth_params when not authenticated."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client._get_auth_params()


class TestGuacamoleAPIClientGetConnectionGroups:
    """Tests for GuacamoleAPIClient.get_connection_groups."""

    def test_successful_retrieval(self, authenticated_client):
        """Test successful retrieval of connection groups."""
        with patch("requests.Session.get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = [
                {"identifier": "1", "name": "Group 1"},
                {"identifier": "2", "name": "Group 2"},
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = authenticated_client.get_connection_groups()

            # Verify the request was made with correct parameters
            mock_get.assert_called_once_with(
                "http://localhost:8080/guacamole/api/session/data/mysql/connectionGroups",
                params={"token": "mock-token"},
            )

            # Verify the result
            assert len(result) == 2
            assert result[0]["name"] == "Group 1"
            assert result[1]["name"] == "Group 2"

    def test_authentication_failure(self, client):
        """Test behavior when called without prior authentication."""
        with pytest.raises(
            ValueError, match="Not authenticated. Call authenticate\\(\\) first."
        ):
            client.get_connection_groups()

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
                params={"token": "mock-token"},
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
                params={"token": "mock-token"},
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
