"""Test fixtures for Guacamole API client tests."""

import pytest
from requests.exceptions import RequestException
import responses
from responses import matchers

# Configuration constants
BASE_URL = "http://localhost:8080/guacamole/api"


@pytest.fixture
def api_responses(responses):
    responses.assert_all_requests_are_fired = False
    return responses


@pytest.fixture
def auth_data():
    """Fixture for authentication data."""
    return {
        "username": "guacadmin",
        "password": "guacadmin",
        "token": "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0",
        "response": {
            "authToken": "374C043A320CE19FF4CA0164259B9F4900EFD43F3CC58F73C1EDAC647041F5D0",
            "username": "guacadmin",
            "dataSource": "postgresql",
            "availableDataSources": ["postgresql", "postgresql-shared"],
        },
    }


@pytest.fixture
def client():
    """Fixture for creating a GuacamoleAPIClient instance."""
    from guacamole_csv_importer.api_client import GuacamoleAPIClient

    return GuacamoleAPIClient(
        base_url=BASE_URL,
        username="guacadmin",
        password="guacadmin",
    )


@pytest.fixture
def bad_client():
    """Fixture for creating a GuacamoleAPIClient instance."""
    from guacamole_csv_importer.api_client import GuacamoleAPIClient

    return GuacamoleAPIClient(
        base_url=BASE_URL,
        username="admin",
        password="guacadmin",
    )


@pytest.fixture
def authenticated_client(api_responses, auth_data):
    """Fixture for creating an authenticated GuacamoleAPIClient instance."""
    from guacamole_csv_importer.api_client import GuacamoleAPIClient

    mock_authenticated_response(api_responses, auth_data)
    client = GuacamoleAPIClient(
        base_url=BASE_URL,
        username=auth_data["username"],
        password=auth_data["password"],
    )
    client.authenticate()
    return client


@pytest.fixture
def connection_data():
    """Fixture for connection data used in tests."""
    return {
        "name": "Test Connection",
        "protocol": "ssh",
        "parameters": {
            "hostname": "localhost",
            "port": "22",
            "username": "guest",
            "password": "pass",
        },
    }


def handle_request_exception(func):
    """Decorator to handle RequestException consistently."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            raise ValueError(f"API request failed: {e}")

    return wrapper


def mock_server_error(api_responses, url):
    """Mocks a server error response for a given URL."""
    api_responses.add(
        method=responses.POST, url=url, body=RequestException("Server error")
    )
    api_responses.add(
        method=responses.GET, url=url, body=RequestException("Server error")
    )


def mock_get_connection_groups_response(api_responses, auth_data):
    api_responses.get(
        f"{BASE_URL}/session/data/postgresql/connectionGroups",
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
            matchers.query_param_matcher({"token": auth_data["token"]}),
        ],
    )

    api_responses.get(
        f"{BASE_URL}/session/data/postgresql/connectionGroups",
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


def mock_get_connections_response(api_responses, auth_data):
    api_responses.get(
        f"{BASE_URL}/session/data/postgresql/connections",
        json={
            "1": {
                "name": "connection-1",
                "identifier": "1",
                "parentIdentifier": "ROOT",
                "protocol": "ssh",
                "attributes": {
                    "guacd-encryption": "none",
                    "failover-only": None,
                    "weight": None,
                    "max-connections": None,
                    "guacd-hostname": "guacd",
                    "guacd-port": "4822",
                    "max-connections-per-user": None,
                },
                "activeConnections": 0,
            },
            "2": {
                "name": "connection-2",
                "identifier": "2",
                "parentIdentifier": "ROOT",
                "protocol": "ssh",
                "attributes": {
                    "guacd-encryption": "none",
                    "failover-only": None,
                    "weight": None,
                    "max-connections": None,
                    "guacd-hostname": "guacd",
                    "guacd-port": "4822",
                    "max-connections-per-user": None,
                },
                "activeConnections": 0,
            },
        },
        match=[
            matchers.query_param_matcher({"token": auth_data["token"]}),
        ],
    )

    api_responses.get(
        f"{BASE_URL}/session/data/postgresql/connections",
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


def mock_authenticated_response(api_responses, auth_data):
    api_responses.post(
        f"{BASE_URL}/tokens",
        json=auth_data["response"],
        status=200,
        match=[
            matchers.urlencoded_params_matcher(
                {"username": auth_data["username"], "password": auth_data["password"]}
            )
        ],
    )

    api_responses.post(
        f"{BASE_URL}/tokens",
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


def mock_post_connection_create_response(api_responses, auth_data, connection_data):
    request_json = {
        "parentIdentifier": "ROOT",
        "name": connection_data["name"],
        "protocol": connection_data["protocol"],
        "attributes": {
            "guacd-hostname": "guacd",
            "guacd-port": "4822",
            "guacd-encryption": "none",
        },
        "parameters": connection_data["parameters"],
    }

    # clone the request_json to avoid modifying the original
    response_json = request_json.copy()
    response_json["identifier"] = "10"
    response_json["activeConnections"] = 0
    response_json["attributes"] = {"guacd-encryption": "none"}

    api_responses.post(
        f"{BASE_URL}/session/data/postgresql/connections",
        json=response_json,
        status=200,
        match=[
            matchers.query_param_matcher({"token": auth_data["token"]}),
            matchers.header_matcher({"Content-Type": "application/json"}),
            matchers.json_params_matcher(request_json, strict_match=False),
        ],
    )

    api_responses.post(
        f"{BASE_URL}/session/data/postgresql/connections",
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


def mock_post_connection_group(api_responses, auth_data, group_name="test-group-1"):
    request_json = {
        "parentIdentifier": "ROOT",
        "name": group_name,
        "type": "ORGANIZATIONAL",
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "enable-session-affinity": "",
        },
    }
    response_json = {
        "name": group_name,
        "identifier": "20",
        "parentIdentifier": "ROOT",
        "type": "ORGANIZATIONAL",
        "activeConnections": 0,
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "enable-session-affinity": "",
        },
    }

    api_responses.post(
        f"{BASE_URL}/session/data/postgresql/connectionGroups",
        json=response_json,
        match=[
            matchers.query_param_matcher({"token": auth_data["token"]}),
            matchers.header_matcher({"Content-Type": "application/json"}),
            matchers.json_params_matcher(request_json, strict_match=False),
        ],
    )

    api_responses.post(
        f"{BASE_URL}/session/data/postgresql/connectionGroups",
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


@pytest.fixture
def default_connection_group():
    return [
        {
            "name": "c8k",
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
        {
            "name": "n9k",
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
        {
            "name": "xrv",
            "identifier": "3",
            "parentIdentifier": "ROOT",
            "type": "ORGANIZATIONAL",
            "activeConnections": 0,
            "attributes": {
                "max-connections": None,
                "max-connections-per-user": None,
                "enable-session-affinity": "",
            },
        },
    ]


@pytest.fixture
def default_connections():
    return [
        {
            "name": "lnx-1",
            "identifier": "7",
            "parentIdentifier": "ROOT",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "c8k-1",
            "identifier": "1",
            "parentIdentifier": "1",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "c8k-2",
            "identifier": "2",
            "parentIdentifier": "1",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "n9k-1",
            "identifier": "3",
            "parentIdentifier": "2",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "n9k-2",
            "identifier": "4",
            "parentIdentifier": "2",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "xrv-1",
            "identifier": "5",
            "parentIdentifier": "3",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
        {
            "name": "xrv-2",
            "identifier": "6",
            "parentIdentifier": "3",
            "protocol": "ssh",
            "attributes": {
                "guacd-encryption": "none",
                "failover-only": "true",
                "weight": None,
                "max-connections": "15",
                "guacd-hostname": "guacd",
                "guacd-port": "4822",
                "max-connections-per-user": "1",
            },
            "activeConnections": 0,
            "lastActive": 1742057190918,
        },
    ]
