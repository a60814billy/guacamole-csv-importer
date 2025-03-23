import os
from unittest.mock import MagicMock

import pytest

from guacamole_csv_importer.importer import ConnectionImporter


@pytest.fixture
def fake_api_client(default_connection_group, default_connections):
    class FakeApiClient:
        def __init__(self):
            self.authenticate = MagicMock(return_value=True)
            self.get_connection_groups = MagicMock(
                return_value=default_connection_group
            )
            self.get_connections = MagicMock(return_value=default_connections)
            self.create_connection = MagicMock(return_value=True)
            self.create_connection_group = MagicMock(return_value=True)

    return FakeApiClient()


# create fake api client


def test_importer(fake_api_client):
    test_csv_path = os.path.join(os.path.dirname(__file__), "fixture/connections_1.csv")
    fake_api_client.create_connection_group = MagicMock(return_value="10")
    fake_api_client.create_connection = MagicMock(return_value="100")

    importer = ConnectionImporter(fake_api_client)
    importer.import_connections(test_csv_path)

    assert importer is not None
