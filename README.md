# Guacamole CSV Importer (gu-import)

A Python package for importing connections from CSV files into Apache Guacamole.

## Features

- Import connections from CSV files into Apache Guacamole
- Create hierarchical connection groups automatically from CSV structure
- Command-line interface for easy use

## Installation

### Requirements

- Python 3.8 or higher
- Apache Guacamole server

### From Source

```bash
pip3 install git+https://github.com/a60814billy/guacamole-csv-importer.git@v0.1.1
```

## Usage

### Command-line Interface

The package installs a command-line tool called `gu-import`:

```bash
gu-import connections.csv --url http://localhost:8080/guacamole/api --username admin --password password
```

#### Options

- `csv_file`: Path to the CSV file containing connection data
- `--url`, `-u`: Base URL of the Guacamole API
- `--username`, `-n`: Guacamole admin username
- `--password`, `-p`: Guacamole admin password
- `--version`: Show version information

## CSV File Format

The CSV file should have the following columns:

- `site`: Hierarchical path for connection groups (e.g., "DC1/Rack1")
- `device_name`: Name of the connection
- `hostname`: Hostname or IP address of the target
- `protocol`: Protocol to use (e.g., `ssh`, `telnet`, `vnc`, `rdp`)
- `port`: Port number to connect to
- `username`: Username for the connection
- `password`: Password for the connection

Example CSV (Check the `connections-example.csv` file):

```csv
site,device_name,hostname,protocol,port,username,password
DC1/Rack1,sw-01,192.168.1.1,ssh,22,admin,admin
DC1/Rack2,sw-02,192.168.1.2,ssh,22,admin,admin
```

In this example:
- Connections will be organized in a hierarchical structure (DC1 → Rack1 → sw-01)
- Each row represents a connection with its authentication credentials
- The `site` column determines the connection group structure

## Development

### Requirement
- uv

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/a60814billy/guacamole-csv-importer.git
cd guacamole-csv-importer

# Install development dependencies
uv sync --all-extras

# active venv
source .venv/bin/activate
```

### Running Tests

```bash
pytest
# or 
uv run pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
