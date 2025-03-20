import pytest
from guacamole_csv_importer.connection_group_tree import ConnectionGroupTree


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


def test_connection_group_tree(default_connection_group, default_connections):
    tree = ConnectionGroupTree()
    tree.build_from_data(default_connection_group, default_connections)

    c8k_grp = tree.find_group("1")
    assert tree.reverse_get_full_path_name(c8k_grp) == "ROOT/c8k"

    assert tree.path_mapping["ROOT/c8k"] == c8k_grp

    tree.print_tree()
