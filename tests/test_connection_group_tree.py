import pytest
from guacamole_csv_importer.connection_group_tree import ConnectionGroupTree


def test_connection_group_tree(default_connection_group, default_connections):
    tree = ConnectionGroupTree()
    tree.build_from_data(default_connection_group, default_connections)

    c8k_grp = tree.find_group("1")
    assert tree.reverse_get_full_path_name(c8k_grp) == "ROOT/c8k"

    assert tree.path_mapping["ROOT/c8k"] == c8k_grp

    tree.print_tree()
