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

You can also specify guacd configuration options:

```bash
gu-import connections.csv --url http://localhost:8080/guacamole/api --username admin --password password \
  --guacd-host guacd.example.com --guacd-port 4822 --guacd-encryption ssl
```

#### Options

- `csv_file`: Path to the CSV file containing connection data
- `--url`: Base URL of the Guacamole API
- `--username`, `-u`: Guacamole admin username
- `--password`, `-p`: Guacamole admin password
- `--guacd-host`: Hostname or IP address of the guacd server (default: localhost)
- `--guacd-port`: Port on which guacd is listening (default: 4822)
- `--guacd-encryption`: Encryption method to use for guacd connection (choices: none, ssl, default: none)
- `--verbose`, `-v`: Enable verbose logging
- `--version`: Show version information

You can also set these options using environment variables:
- `GUACD_HOST`: Hostname or IP address of the guacd server
- `GUACD_PORT`: Port on which guacd is listening
- `GUACD_ENCRYPTION`: Encryption method to use for guacd connection

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
