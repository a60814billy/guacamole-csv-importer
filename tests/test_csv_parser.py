"""Tests for the CSV parser module."""

from pathlib import Path

import pytest

from guacamole_csv_importer.csv_parser import CSVParser


def test_validate_headers_valid():
    """Test that validate_headers returns True for valid headers."""
    parser = CSVParser(Path("dummy.csv"))
    headers = [
        "site",
        "device_name",
        "protocol",
        "port",
        "hostname",
        "username",
        "password",
    ]
    assert parser.validate_headers(headers) is True


def test_validate_headers_invalid():
    """Test that validate_headers returns False for invalid headers."""
    parser = CSVParser(Path("dummy.csv"))
    headers = ["name", "protocol", "hostname"]  # Missing "port"
    assert parser.validate_headers(headers) is False


def test_process_row_valid():
    """Test that _process_row correctly processes a valid row."""
    parser = CSVParser(Path("dummy.csv"))
    row = {
        "site": "Test Site",
        "device_name": "Test Server",
        "protocol": "ssh",
        "port": "22",
        "hostname": "192.168.1.1",
        "username": "admin",
        "password": "password",
    }
    result = parser._process_row(row)
    assert result["site"] == "Test Site"
    assert result["device_name"] == "Test Server"
    assert result["protocol"] == "ssh"
    assert result["port"] == "22"
    assert result["hostname"] == "192.168.1.1"
    assert result["username"] == "admin"
    assert result["password"] == "password"


def test_process_row_missing_required():
    """Test that _process_row raises ValueError for missing required fields."""
    parser = CSVParser(Path("dummy.csv"))
    row = {
        "name": "Test Server",
        "protocol": "rdp",
        "hostname": "",  # Empty required field
        "port": "3389",
    }
    with pytest.raises(ValueError):
        parser._process_row(row)
