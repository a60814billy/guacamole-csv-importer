"""Setup script for Guacamole CSV Importer."""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join("guacamole_csv_importer", "__init__.py"), "r") as f:
    version_match = re.search(r'__version__ = "(.*?)"', f.read())
    version = version_match.group(1) if version_match else "0.1.0"

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="guacamole-csv-importer",
    version=version,
    description="Import connections from CSV files into Apache Guacamole",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/guacamole-csv-importer",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "guacamole-csv-import=guacamole_csv_importer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Systems Administration",
    ],
    keywords="guacamole, csv, import, remote desktop",
)
