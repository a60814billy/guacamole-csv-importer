# Guacamole CSV Importer

A Python package for importing connections from CSV files into Apache Guacamole.

## Features

- Import connections from CSV files into Apache Guacamole
- Create connection groups to organize connections
- Validate CSV files before import
- Command-line interface for easy use
- Detailed logging for troubleshooting

## Installation

### From PyPI

```bash
pip install guacamole-csv-importer
```

### From Source

```bash
git clone https://github.com/yourusername/guacamole-csv-importer.git
cd guacamole-csv-importer
pip install -e .
```

## Usage

### Command-line Interface

```bash
guacamole-csv-import connections.csv --url http://localhost:8080/guacamole/api --username admin --password password
```

#### Options

- `csv_file`: Path to the CSV file containing connection data
- `--url`, `-u`: Base URL of the Guacamole API
- `--username`, `-n`: Guacamole admin username
- `--password`, `-p`: Guacamole admin password
- `--parent-group`, `-g`: Name of the parent connection group to create (optional)
- `--verbose`, `-v`: Enable verbose logging
- `--version`: Show version information

### Python API

```python
from pathlib import Path
from guacamole_csv_importer.importer import ConnectionImporter

# Create importer
importer = ConnectionImporter(
    api_url="http://localhost:8080/guacamole/api",
    username="admin",
    password="password",
    csv_file=Path("connections.csv"),
    parent_group="Imported Connections"
)

# Import connections
successful, total = importer.import_connections()
print(f"Imported {successful}/{total} connections")
```

## CSV File Format

The CSV file should have the following columns:

- `name`: Name of the connection
- `protocol`: Protocol to use (e.g., `rdp`, `ssh`, `vnc`)
- `hostname`: Hostname or IP address of the target
- `port`: Port number to connect to

Additional columns will be added as connection parameters.

Example:

```csv
name,protocol,hostname,port,username,password,domain
Server 1,rdp,192.168.1.100,3389,admin,password,example.com
Server 2,ssh,192.168.1.101,22,user,password,
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/guacamole-csv-importer.git
cd guacamole-csv-importer

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
