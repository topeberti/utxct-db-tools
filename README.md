# SQL Database for UT and XCT Data Management

This repository contains tools and notebooks for managing, loading, retrieving, and analyzing ultrasound testing (UT) and X-ray computed tomography (XCT) data in a PostgreSQL database.

## Overview

The system is designed to store and manage various types of data including:
- Material specifications
- Panel information
- Sample details
- UT and XCT measurements
- Dataset information
- Measurement registrations

## Setup

### Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python packages (install via pip):
  - psycopg2
  - numpy
  - pandas
  - tifffile
  - tabulate
  - tqdm

### Environment Configuration

1. Create an `.env` file in the root directory based on the provided example:

DB_HOST=airbus-pc DB_NAME=UTvsXCT DB_USER=username DB_PASSWORD=password


2. Replace the placeholder values with your actual database credentials.

## Project Structure

- `dbtools/`: Contains database utility functions
- `load/`: Notebooks for data loading
  - `materials.ipynb`: For loading material information
  - `panel.ipynb`: For loading panel data
  - `sample.ipynb`: For loading sample information
  - `measurements_ut.ipynb`: For loading UT measurement data
  - `measurements_xct.ipynb`: For loading XCT measurement data
  - `datasets.ipynb`: For loading dataset information
  - `registrations.ipynb`: For loading measurement registrations
- `retrieve/`: Notebooks for data retrieval
  - `data.ipynb`: Basic data retrieval
  - `data_metadata.ipynb`: Retrieval with metadata
  - `data_relation.ipynb`: Retrieval of related data
- `migration/`: Notebooks for data migration
- `delete/`: Notebooks for data deletion examples

## Usage Examples

### Connecting to the Database

```python
import dbtools.dbtools as qrs

try:
    conn = qrs.connect()
    print("Connected to the database")
except Exception as error:
    print(error)