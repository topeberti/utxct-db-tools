# imports
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional, Any, Union

# Global variable to store the environment path
_ENV_PATH = None

def load_credentials(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Loads the database credentials from a .env file.

    Parameters:
    env_path (Optional[str]): The path to the .env file. If None, uses default location.

    Returns:
    Dict[str, str]: A dictionary containing the database credentials.
    """
    global _ENV_PATH
    
    # Update global env_path if a new path is provided
    if env_path is not None and env_path != _ENV_PATH:
        _ENV_PATH = env_path
        # Load the environment variables from the specified .env file
        load_dotenv(env_path)
    else:
        # Load from default location or previously set _ENV_PATH
        load_dotenv(_ENV_PATH)

    # Return dictionary with credentials from environment variables
    return {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

def connect(env_path: Optional[str] = None) -> psycopg2.extensions.connection:
    """
    Establishes a connection to the PostgreSQL database.

    Parameters:
    env_path (Optional[str]): Path to the environment file containing credentials.
                             If None, uses the globally stored path.

    Returns:
    psycopg2.extensions.connection: A connection object to the PostgreSQL database.
    """
    # Load credentials from environment file
    credentials = load_credentials(env_path)

    # Establish database connection using credentials
    conn = psycopg2.connect(
        host=credentials['host'],
        database=credentials['database'],
        user=credentials['user'],
        password=credentials['password'])
    return conn

# DATAFRAME MANAGEMENT

def metadata_add(data: pd.DataFrame, metadata: pd.DataFrame, id_column_name: str) -> pd.DataFrame:
    """
    Adds metadata to the data dataframe.

    Parameters:
    data (pd.DataFrame): The main data dataframe.
    metadata (pd.DataFrame): The metadata dataframe.
    id_column_name (str): The column name in metadata that corresponds to the id in data.

    Returns:
    pd.DataFrame: The data dataframe with metadata added.
    """
    # Get the id column of data
    ids = data['id']

    # Loop through each ID to add its metadata
    for id in ids:
        # Get the metadata where the id is equal to the value in id_column_name
        metadata_id = metadata[metadata[id_column_name] == id]

        # Iterate over the rows of the metadata_id
        for index, row in metadata_id.iterrows():
            column_name = row['key']
            value = row['value']
            units = row['type']
            # Add metadata value with units to the data frame
            data.loc[data['id'] == id, column_name] = str(value) + ' ' + units 

    return data

def parent_add(data: pd.DataFrame, parent_data: pd.DataFrame, 
               column_parent_id_name: str, suffixes: tuple = ('_data', '_parent')) -> pd.DataFrame:
    """
    Concatenates a parent dataframe to the main data dataframe.

    Parameters:
    data (pd.DataFrame): The main data dataframe.
    parent_data (pd.DataFrame): The parent data dataframe.
    column_parent_id_name (str): The column name in data that corresponds to the id in parent_data.
    suffixes (tuple): Suffixes to apply to overlapping column names in the left and right side, respectively.

    Returns:
    pd.DataFrame: The concatenated dataframe with parent data joined.
    """
    # Merge the data and parent_data dataframes based on the specified column
    merged_data = pd.merge(data, parent_data, left_on=column_parent_id_name, 
                          right_on='id' + suffixes[1], how='inner', suffixes=suffixes)

    # Drop the column used for joining to avoid duplication
    merged_data.drop(columns=[column_parent_id_name], inplace=True)

    return merged_data

# QUERY FUNCTIONS

def get_data(table_name: str) -> pd.DataFrame:
    """
    Loads data from a specified table in the database.

    Parameters:
    table_name (str): The name of the table to load data from.

    Returns:
    pd.DataFrame: The loaded data as a pandas dataframe.
    """
    # Connect to the database
    try:
        conn = connect()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Create SQL query to select all data from the specified table
    query = f"SELECT * FROM {table_name}"

    # Execute the query
    cursor.execute(query)

    # Fetch all the records
    records = cursor.fetchall()

    # Get the column names
    colnames = [desc[0] for desc in cursor.description]

    # Create a pandas dataframe from the records
    data = pd.DataFrame(records, columns=colnames)

    # Remove columns that are entirely NaN values
    data = data.dropna(axis=1, how='all')

    # Rename columns to include the table name
    data.columns = [str(col) + '_' + table_name[:-1] for col in data.columns]

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    return data

def get_data_metadata(table_name: str) -> pd.DataFrame:
    """
    Loads data and its metadata from specified tables in the database.

    Parameters:
    table_name (str): The name of the table to load data from.

    Returns:
    pd.DataFrame: The loaded data with metadata as a pandas dataframe.
    """
    # Construct metadata table name by replacing 's' with '_metadata'
    metadata_name = table_name[:-1] + '_metadata'
    
    # Construct ID column name for metadata
    id_column_name = table_name[:-1] + '_id'

    # Connect to the database
    try:
        conn = connect()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Fetch data from main table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    records = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    data = pd.DataFrame(records, columns=colnames)

    # Fetch data from metadata table
    query = f"SELECT * FROM {metadata_name}"
    cursor.execute(query)
    records = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    metadata = pd.DataFrame(records, columns=colnames)

    # Join metadata with main data
    data = metadata_add(data, metadata, id_column_name)

    # Remove columns that are entirely NaN values
    data = data.dropna(axis=1, how='all')

    # Rename columns to include the table name
    data.columns = [str(col) + '_' + table_name[:-1] for col in data.columns]

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    return data

def data_parent(table_name: str, parent_name: str, column_parent_id_name: Optional[str] = None) -> pd.DataFrame:
    """
    Loads data, its metadata, and parent data from specified tables in the database.

    Parameters:
    table_name (str): The name of the table to load data from.
    parent_name (str): The name of the parent table to load data from.
    column_parent_id_name (Optional[str]): The column name in data that corresponds to the id in parent_data.
                                          If None, it's automatically generated.

    Returns:
    pd.DataFrame: The loaded data with metadata and parent data as a pandas dataframe.
    """
    # Get data with metadata for the main table
    data = get_data_metadata(table_name)
    
    # Get data with metadata for the parent table
    parent_data = get_data_metadata(parent_name)

    # If parent ID column name is not provided, generate it
    if column_parent_id_name is None:
        column_parent_id_name = parent_name[:-1] + '_id'

    # Adjust column name to include table suffix
    column_parent_id_name = column_parent_id_name + '_' + table_name[:-1]
    
    # Define suffixes for the merged columns
    suffixes = ('_' + table_name[:-1], '_' + parent_name[:-1])

    # Merge the data and parent dataframes
    merged_data = parent_add(data, parent_data, column_parent_id_name, suffixes=suffixes)

    # Remove columns that are entirely NaN values
    merged_data = merged_data.dropna(axis=1, how='all')

    return merged_data

def multiple_parents(table_name: str, parents_names: List[str], 
                    column_parent_id_names: List[str]) -> pd.DataFrame:
    """
    Loads data, its metadata, and multiple parent data from specified tables in the database.

    Parameters:
    table_name (str): The name of the table to load data from.
    parents_names (List[str]): The names of the parent tables to load data from.
    column_parent_id_names (List[str]): The column names in data that correspond to the ids in parent_data.

    Returns:
    pd.DataFrame: The loaded data with metadata and multiple parent data as a pandas dataframe.
    """
    # Generate suffixes for column naming
    suffixes = [''] + ['_' + name[:-1] for name in parents_names]
    
    # Create suffix pairs for merging
    suffixes_list = []
    for i, value in enumerate(suffixes):
        if i == 0:
            suffixes_list.append([value, suffixes[i+1]])
        elif i > 1:
            suffixes_list.append(['', value])

    # Get data with metadata for the main table
    data = get_data_metadata(table_name)

    # Iteratively merge each parent table
    for parent_name, column_parent_id_name, suffix in zip(parents_names, column_parent_id_names, suffixes_list):
        # Get data for the current parent
        parent_data = get_data_metadata(parent_name)
        
        # Merge parent data with the main dataset
        data = parent_add(data, parent_data, column_parent_id_name, suffixes=suffix)
    
    # Remove columns that are entirely NaN values
    data = data.dropna(axis=1, how='all')
    
    return data

def relation_metadata(table1_name: str, table2_name: str, intermediate_table_name: str) -> pd.DataFrame:
    """
    Loads data from two tables related by an intermediate relationship table.

    Parameters:
    table1_name (str): The name of the first table to load data from.
    table2_name (str): The name of the second table to load data from.
    intermediate_table_name (str): The name of the intermediate relationship table.

    Returns:
    pd.DataFrame: The loaded data with metadata from the two related tables as a pandas dataframe.
    """
    # Generate column names for join conditions
    column_id_1 = table1_name[:-1] + '_id'
    column_id_2 = table2_name[:-1] + '_id'

    # Get data with metadata for both main tables
    data1 = get_data_metadata(table1_name)
    data2 = get_data_metadata(table2_name)
    
    # Get data from the intermediate table
    intermediate_data = get_data(intermediate_table_name)

    #check if the intermediate table is empty
    if intermediate_data.empty:
        raise ValueError(f"The intermediate table '{intermediate_table_name}' is empty. Cannot perform relation merge.")
    
    # Remove the ID column from intermediate data
    intermediate_data = intermediate_data.drop(columns=['id_'+intermediate_table_name[:-1]])
    
    # Define suffixes for column naming
    suffixes = ('_' + table1_name[:-1], '_' + table2_name[:-1])
    
    # Perform the first merge between data1 and intermediate data
    merged_data = pd.merge(
        data1, 
        intermediate_data, 
        left_on='id_' + table1_name[:-1], 
        right_on=column_id_1 + '_' + intermediate_table_name[:-1], 
        how='inner', 
        suffixes=('', suffixes[0])
    )
    
    # Perform the second merge to include data2
    merged_data = pd.merge(
        merged_data, 
        data2, 
        left_on=column_id_2+ '_' + intermediate_table_name[:-1], 
        right_on='id_' + table2_name[:-1], 
        how='inner', 
        suffixes=('', suffixes[1])
    )
    
    # Remove intermediate table columns from the result
    merged_data = merged_data.drop(columns=[c for c in intermediate_data.columns])
    
    # Remove columns that are entirely NaN values
    merged_data = merged_data.dropna(axis=1, how='all')
    
    return merged_data

def get_id(table_name,keys,values):

    """
    Retrieves the ID from a specified table based on given keys and values.

    Parameters:
    table_name (str): The name of the table to query.
    keys (List[str]): The list of column names to filter by.
    values (List[Any]): The corresponding values for the keys.

    Returns:
    int: The ID from the specified table that matches the given keys and values.
    """

    #assert that the table_name is a string
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")
    #assert that keys and values are lists
    if not isinstance(keys, list) or not isinstance(values, list):
        raise TypeError("keys and values must be lists")
    #assert that keys and values have the same length
    if len(keys) != len(values):
        raise ValueError("keys and values must have the same length")

    #get the table as a dataframe
    data = get_data_metadata(table_name)

    #Filter the dataframe based on the keys and values

    filtered_data = data

    for key, value in zip(keys, values):
        filtered_data = filtered_data[filtered_data[key] == value]
    
    #If no rows match, raise an error
    if filtered_data.empty:
        raise ValueError(f"No matching record found in {table_name} for keys {keys} with values {values}")  
    
    #If multiple rows match, raise an error
    if len(filtered_data) > 1:
        raise ValueError(f"Multiple records found in {table_name} for keys {keys} with values {values}")
    
    #Return the ID of the first row
    return filtered_data['id_' + table_name[:-1]].values[0]
    