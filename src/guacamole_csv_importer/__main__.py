"""Main entry point for Guacamole CSV Importer.

This module allows the package to be run as a module:
python -m guacamole_csv_importer
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
