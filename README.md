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

## Setup

### Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python packages:
  - psycopg2
  - numpy
  - pandas
  - tifffile
  - tabulate
  - tqdm

#### Installing Python Dependencies

You can install all required packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Alternatively, you can install packages individually:

```bash
pip install psycopg2 numpy pandas tifffile tabulate tqdm
```

### Environment Configuration

1. Create an `.env` file in the root directory based (if the file is not in the directory its path may be required by some functions) on the provided example:
```python
DB_HOST=airbus-pc 
DB_NAME=UTvsXCT 
DB_USER=username 
DB_PASSWORD=password
```
2. Replace the placeholder values with your actual database credentials.

### Installing as a Python Module

You can install this repository as a Python module directly from GitHub:

```bash
pip install git+https://github.com/topeberti/utxct-db-tools.git
```

#### Benefits of Installing as a Module

Installing the repository as a Python module provides several advantages:

1. **System-wide Availability**: The package becomes available system-wide, allowing you to import it from any Python script or notebook without worrying about file paths.

2. **Improved Import Structure**: You can use clean import statements like `import utxct_db_tools` instead of using relative or absolute imports.

3. **Version Management**: You can specify version requirements in other projects that depend on this package.

4. **Easy Updates**: Update the package with a simple pip command without manually downloading or pulling changes:
   ```bash
   pip install --upgrade git+https://github.com/topeberti/utxct-db-tools.git
   ```

#### Using the Installed Module

After installation, you can import and use the module in your Python scripts or notebooks:

```python
# Import the main database tools module
import dbtools as db

# Connect to the database
conn = db.connect('path_to_env/.env')

# Retrieve data
samples = db.get_data('samples')

# Get data with metadata
samples_with_metadata = db.get_data_metadata('samples')

# Close the connection when done
conn.close()
```

This approach makes your code more portable and maintainable compared to using relative imports.

## Usage Examples

### Connecting to the Database

```python
import dbtools.dbtools as qrs

try:
    conn = qrs.connect()
    print("Connected to the database")
except Exception as error:
    print(error)
```