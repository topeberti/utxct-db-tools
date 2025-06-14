"""
Database Loading Module

This module provides functions to securely load data into the database.
It includes functions to load rows into tables, as well as specialized
functions to load materials and panels with their associated metadata.

Dependencies:
    - dbtools: Custom database utility module
"""

import dbtools as dbt

def load_table(cursor, table_name, data):
    """
    Load a single row of data into a database table.
    
    Parameters:
    -----------
    cursor : psycopg2.cursor
        An active database cursor object.
    table_name : str
        The name of the table to insert data into.
    data : dict
        Dictionary with column names as keys and values to insert.
        
    Returns:
    --------
    int
        The ID of the inserted row.
        
    Raises:
    -------
    ValueError
        If the cursor is invalid or data is not a dictionary.
    Exception
        Any database errors that occur during execution.
    """
    # Validate cursor by executing a simple query
    try:
        cursor.execute("SELECT 1")
    except Exception as e:
        raise ValueError("Invalid cursor: " + str(e))
    
    # Check that data is a dictionary
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
        
    # Extract column names and values from the attributes dictionary
    columns = ', '.join(data.keys())
    placeholders = ', '.join(["%s" for _ in data.values()])
    values = list(data.values())

    # Construct the SQL INSERT statement with RETURNING clause
    # Assuming the ID column follows the pattern 'id'
    id_column = f"id"
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING {id_column}"

    # Execute the SQL statement with parameterized query
    cursor.execute(sql, values)

    # Fetch the returned ID
    inserted_id = cursor.fetchone()[0]
    
    return inserted_id


def load_material(conn, name, layer_thickness, layer_layout):
    """
    Load a material into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    name : str
        Material name.
    layer_thickness : float
        Thickness of the material layer.
    layer_layout : list
        List of integers representing the layer layout.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(name, str) and name, "Material name must be a non-empty string"
    assert isinstance(layer_thickness, (float, int)) and layer_thickness > 0, "Layer thickness must be a positive number"
    assert isinstance(layer_layout, list) and all(isinstance(i, int) for i in layer_layout), "Layer layout must be a list of integers"

    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction

    # Create the parameters dictionary for material insertion
    parameters = {
        'name': name
    }
    
    # Load the material into the database
    table_name = 'materials'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading material: {e}")
        conn.rollback()
        cursor.close()
        return

    print(f"Material '{name}' loaded with ID: {row_id}")

    # Query metadata table (this appears to be unused)
    cursor.execute("select * from material_metadata")

    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id':row_id, 'key': 'layer_thickness', 'value': layer_thickness, 'type': 'float'},
        {table_name[:-1] + '_id':row_id, 'key': 'layer_layout', 'value': str(layer_layout), 'type': 'list'}
    ]

    metadata_table_name = 'material_metadata'

    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()

    # Close the cursor
    cursor.close()


def load_panel(conn, name, material_id, dimensions, edges_cutted, description=None):
    """
    Load a panel into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    name : str
        Panel name.
    material_id : int
        ID of the material used in the panel.
    dimensions : list
        List of dimensions in (x,y,z) format in millimeters.
    edges_cutted : bool
        Whether the edges are cutted.
    description : str, optional
        Panel description.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(name, str) and name, "Panel name must be a non-empty string"
    assert isinstance(material_id, int) and material_id > 0, "Material ID must be a positive integer"
    assert isinstance(dimensions, list) and len(dimensions) == 3, "Dimensions must be a list of 3 values (x,y,z)"
    assert all(isinstance(d, (float, int)) for d in dimensions), "Dimensions must be numeric values"
    assert isinstance(edges_cutted, bool), "edges_cutted must be a boolean"
    
    # Validate description if provided
    if description is not None:
        assert isinstance(description, str), "Description must be a string"
    
    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction
    
    # Create the parameters dictionary for panel insertion
    parameters = {
        'name': name,
        'material_id': material_id
    }
    
    # Add description if provided
    if description is not None:
        parameters['description'] = description
    
    # Load the panel into the database
    table_name = 'panels'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading panel: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"Panel '{name}' loaded with ID: {row_id}")
    
    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id': row_id, 'key': 'dim', 'value': str(dimensions), 'type': 'mm'},
        {table_name[:-1] + '_id': row_id, 'key': 'edges_cutted', 'value': str(edges_cutted), 'type': 'bool'}
    ]
    
    metadata_table_name = 'panel_metadata'
    
    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading panel metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()


def load_sample(conn, name, panel_id, height, width, thickness, keyhole, parallel_faces, description=None):
    """
    Load a sample into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    name : str
        Sample name.
    panel_id : int
        ID of the panel from which the sample is taken.
    height : float
        Height of the sample in millimeters.
    width : float
        Width of the sample in millimeters.
    thickness : float
        Thickness of the sample in millimeters.
    keyhole : bool
        Whether the sample has keyholes.
    parallel_faces : bool
        Whether the sample has parallel faces.
    description : str, optional
        Sample description.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(name, str) and name, "Sample name must be a non-empty string"
    assert isinstance(panel_id, int) and panel_id > 0, "Panel ID must be a positive integer"
    assert isinstance(height, (float, int)) and height > 0, "Height must be a positive number"
    assert isinstance(width, (float, int)) and width > 0, "Width must be a positive number"
    assert isinstance(thickness, (float, int)) and thickness > 0, "Thickness must be a positive number"
    assert isinstance(keyhole, bool), "keyhole must be a boolean"
    assert isinstance(parallel_faces, bool), "parallel_faces must be a boolean"
    
    # Validate description if provided
    if description is not None:
        assert isinstance(description, str), "Description must be a string"
    
    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction
    
    # Create the parameters dictionary for sample insertion
    parameters = {
        'name': name,
        'panel_id': panel_id
    }
    
    # Add description if provided
    if description is not None:
        parameters['description'] = description
    
    # Load the sample into the database
    table_name = 'samples'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading sample: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"Sample '{name}' loaded with ID: {row_id}")
    
    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id': row_id, 'key': 'height', 'value': str(height), 'type': 'mm'},
        {table_name[:-1] + '_id': row_id, 'key': 'width', 'value': str(width), 'type': 'mm'},
        {table_name[:-1] + '_id': row_id, 'key': 'thickness', 'value': str(thickness), 'type': 'mm'},
        {table_name[:-1] + '_id': row_id, 'key': 'keyhole', 'value': str(keyhole), 'type': 'bool'},
        {table_name[:-1] + '_id': row_id, 'key': 'parallel_faces', 'value': str(parallel_faces), 'type': 'bool'}
    ]
    
    metadata_table_name = 'sample_metadata'
    
    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading sample metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()


def load_ut_measurement(conn, file_path, measurementtype_id, height, width, depth, dtype, 
                        file_type, signal_type, axes_order,sample_names, parent_measurement_path=None, transformations=None):
    """
    Load an ultrasonic measurement into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    file_path : str
        The path to the measurement file.
    measurementtype_id : int
        ID of the measurement technique used to acquire this measurement.
    height : int
        Height of the measurement.
    width : int
        Width of the measurement.
    depth : int
        Depth of the measurement.
    dtype : str
        Data type of the measurement.
    file_type : str
        File extension of the measurement.
    signal_type : str
        Signal type of the measurement, can only be 'RF' or 'Amplitude'.
    axes_order : list
        Order of the axes of the volume, e.g., ['x', 'y', 'z'].
    sample_names : list
        List of sample names associated with this measurement.
    parent_measurement_path : str, optional
        File path of the parent measurement from which this measurement is derived.
    transformations : str, optional
        Explanation of the transformations done to the parent measurement to create this one.
        Required if parent_measurement_path is set.

    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(file_path, str) and file_path, "File path must be a non-empty string"
    assert isinstance(measurementtype_id, int) and measurementtype_id > 0, "Measurement type ID must be a positive integer"
    assert isinstance(height, int) and height > 0, "Height must be a positive integer"
    assert isinstance(width, int) and width > 0, "Width must be a positive integer"
    assert isinstance(depth, int) and depth > 0, "Depth must be a positive integer"
    assert isinstance(dtype, str), "Data type must be a string"
    assert isinstance(file_type, str), "File type must be a string"
    assert isinstance(signal_type, str), "Signal type must be a string"
    assert signal_type in ['RF', 'Amplitude'], "Signal type must be either 'RF' or 'Amplitude'"
    assert isinstance(axes_order, list) and len(axes_order) > 0, "Axes order must be a non-empty list"
    assert all(isinstance(axis, str) for axis in axes_order), "All axes must be strings"

    # Check parent_measurement_path and transformations
    if parent_measurement_path is not None:
        assert isinstance(parent_measurement_path, str) and parent_measurement_path, "Parent measurement path must be a non-empty string"
        assert isinstance(transformations, str) and transformations, "Transformations must be a non-empty string when parent_measurement_path is provided"

    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction
    
    # Create the parameters dictionary for measurement insertion
    parameters = {
        'file_path': file_path,
        'measurementtype_id': measurementtype_id
    }

    #get the parent_measurement_id
    if parent_measurement_path is not None:
        parent_measurement_id = dbt.get_id('measurements', ['file_path_measurement'], [parent_measurement_path])
        parameters['parent_measurement_id'] = int(parent_measurement_id)
    
    # Load the measurement into the database
    table_name = 'measurements'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading UT measurement: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"UT measurement from '{file_path}' loaded with ID: {row_id}")
    
    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id': row_id, 'key': 'height', 'value': str(height), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'width', 'value': str(width), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'depth', 'value': str(depth), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'dtype', 'value': dtype, 'type': 'nominal'},
        {table_name[:-1] + '_id': row_id, 'key': 'file_type', 'value': file_type, 'type': 'nominal'},
        {table_name[:-1] + '_id': row_id, 'key': 'signal_type', 'value': signal_type, 'type': 'nominal'},
        {table_name[:-1] + '_id': row_id, 'key': 'axes_order', 'value': str(axes_order), 'type': 'list'}
    ]
    
    # Add transformations metadata if provided
    if transformations is not None:
        metadata_parameters.append({
            table_name[:-1] + '_id': row_id, 
            'key': 'transformations', 
            'value': transformations, 
            'type': 'text'
        })
    
    metadata_table_name = 'measurement_metadata'
    
    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading UT measurement metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Insert sample names into the ut_measurement_samples table
    samples_data = dbt.get_data_metadata('samples')

    #get the ids of the samples in sample_names
    samples_data = samples_data[samples_data['name_sample'].isin(sample_names)]

    sample_ids = samples_data['id_sample'].values.tolist()

    relational_table_name = 'sample_measurements'

    for sample_id in sample_ids:

        relational_parameters = {'sample_id': sample_id, 'measurement_id': row_id}

        try:
            load_table(cursor, relational_table_name, relational_parameters)
        except Exception as e:
            print(f"Error loading sample-measurement relationship: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()


def load_xct_measurement(conn, file_path, measurementtype_id, height, width, depth, dtype, 
                         file_type, sample_names, aligned, equalized, parent_measurement_path=None, transformations=None):
    """
    Load an X-ray CT measurement into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    file_path : str
        The path to the measurement file.
    measurementtype_id : int
        ID of the measurement technique used to acquire this measurement.
    height : int
        Height of the measurement.
    width : int
        Width of the measurement.
    depth : int
        Depth of the measurement.
    dtype : str
        Data type of the measurement.
    file_type : str
        File extension of the measurement.
    sample_names : list
        List of sample names associated with this measurement.
    aligned : bool
        Whether the volume is frontwall aligned.
    equalized : bool
        Whether the volume is equalized.
    parent_measurement_path : str, optional
        File path of the parent measurement from which this measurement is derived.
    transformations : str, optional
        Explanation of the transformations done to the parent measurement to create this one.
        Required if parent_measurement_path is set.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(file_path, str) and file_path, "File path must be a non-empty string"
    assert isinstance(measurementtype_id, int) and measurementtype_id > 0, "Measurement type ID must be a positive integer"
    assert isinstance(height, int) and height > 0, "Height must be a positive integer"
    assert isinstance(width, int) and width > 0, "Width must be a positive integer"
    assert isinstance(depth, int) and depth > 0, "Depth must be a positive integer"
    assert isinstance(dtype, str), "Data type must be a string"
    assert isinstance(file_type, str), "File type must be a string"
    assert isinstance(sample_names, list) and len(sample_names) > 0, "Sample names must be a non-empty list"
    assert all(isinstance(name, str) for name in sample_names), "All sample names must be strings"
    assert isinstance(aligned, bool), "aligned must be a boolean"
    assert isinstance(equalized, bool), "equalized must be a boolean"
    
    # Check parent_measurement_path and transformations
    if parent_measurement_path is not None:
        assert isinstance(parent_measurement_path, str) and parent_measurement_path, "Parent measurement path must be a non-empty string"
        assert isinstance(transformations, str) and transformations, "Transformations must be a non-empty string when parent_measurement_path is provided"
    
    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction
    
    # Create the parameters dictionary for measurement insertion
    parameters = {
        'file_path': file_path,
        'measurementtype_id': measurementtype_id
    }
    
    # Get the parent_measurement_id if parent_measurement_path is provided
    if parent_measurement_path is not None:
        parent_measurement_id = dbt.get_id('measurements', ['file_path_measurement'], [parent_measurement_path])
        parameters['parent_measurement_id'] = int(parent_measurement_id)
    
    # Load the measurement into the database
    table_name = 'measurements'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading XCT measurement: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"XCT measurement from '{file_path}' loaded with ID: {row_id}")
    
    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id': row_id, 'key': 'height', 'value': str(height), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'width', 'value': str(width), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'depth', 'value': str(depth), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'dtype', 'value': dtype, 'type': 'string'},
        {table_name[:-1] + '_id': row_id, 'key': 'file_type', 'value': file_type, 'type': 'string'},
        {table_name[:-1] + '_id': row_id, 'key': 'aligned', 'value': str(aligned), 'type': 'boolean'},
        {table_name[:-1] + '_id': row_id, 'key': 'equalized', 'value': str(equalized), 'type': 'boolean'}
    ]
    
    # Add transformations metadata if provided
    if transformations is not None:
        metadata_parameters.append({
            table_name[:-1] + '_id': row_id,
            'key': 'transformations',
            'value': transformations,
            'type': 'text'
        })
    
    metadata_table_name = 'measurement_metadata'
    
    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading XCT measurement metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Insert sample names into the xct_measurement_samples table
    samples_data = dbt.get_data_metadata('samples')

    # Get the ids of the samples in sample_names
    samples_data = samples_data[samples_data['name_sample'].isin(sample_names)]

    sample_ids = samples_data['id_sample'].values.tolist()

    relational_table_name = 'sample_measurements'

    for sample_id in sample_ids:
        relational_parameters = {'sample_id': sample_id, 'measurement_id': row_id}

        try:
            load_table(cursor, relational_table_name, relational_parameters)
        except Exception as e:
            print(f"Error loading sample-measurement relationship: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()


def load_dataset(conn, file_path, rows, patch_size, targets, reconstruction_shape, measurement_paths, description=None):
    """
    Load a dataset into the database, including its metadata and measurement relationships.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    file_path : str
        The path to the dataset file.
    rows : int
        Number of rows in the dataset.
    patch_size : str
        Patch size of the dataset.
    targets : list
        List of targets for the dataset.
    reconstruction_shape : tuple
        Shape to see the dataset as an image.
    measurement_paths : list
        List of measurement file paths associated with this dataset.
    description : str, optional
        Dataset description.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(file_path, str) and file_path, "File path must be a non-empty string"
    assert isinstance(rows, int) and rows > 0, "Rows must be a positive integer"
    assert isinstance(patch_size, str), "Patch size must be a string"
    assert isinstance(targets, list) and all(isinstance(target, str) for target in targets), "Targets must be a list of strings"
    assert isinstance(reconstruction_shape, tuple), "Reconstruction shape must be a tuple"
    assert all(isinstance(dim, int) for dim in reconstruction_shape), "All dimensions in reconstruction shape must be integers"
    assert isinstance(measurement_paths, list) and len(measurement_paths) > 0, "Measurement paths must be a non-empty list"
    assert all(isinstance(path, str) for path in measurement_paths), "All measurement paths must be strings"
    
    # Validate description if provided
    if description is not None:
        assert isinstance(description, str), "Description must be a string"
    
    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction
    
    # Create the parameters dictionary for dataset insertion
    parameters = {
        'file_path': file_path
    }
    
    # Add description if provided
    if description is not None:
        parameters['description'] = description
    
    # Load the dataset into the database
    table_name = 'datasets'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"Dataset from '{file_path}' loaded with ID: {row_id}")
    
    # Create the metadata parameters dictionary
    metadata_parameters = [
        {table_name[:-1] + '_id': row_id, 'key': 'rows', 'value': str(rows), 'type': 'cardinal'},
        {table_name[:-1] + '_id': row_id, 'key': 'patch_size', 'value': patch_size, 'type': 'pixels'},
        {table_name[:-1] + '_id': row_id, 'key': 'reconstruction_shape', 'value': str(reconstruction_shape), 'type': 'pixels tuple'}
    ]

    for target in targets:
        metadata_parameters.append({
            table_name[:-1] + '_id': row_id, 
            'key': 'target', 
            'value': target, 
            'type': 'nominal'
        })
    
    metadata_table_name = 'dataset_metadata'
    
    # Insert each metadata entry
    for attributes in metadata_parameters:
        try:
            load_table(cursor, metadata_table_name, attributes)
        except Exception as e:
            print(f"Error loading dataset metadata: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Insert sample names into the xct_measurement_samples table
    measurements_data = dbt.get_data_metadata('measurements')

    # Filter measurements to only include those whose file paths match the provided paths
    measurements_data = measurements_data[measurements_data['file_path_measurement'].isin(measurement_paths)]

    # Extract the measurement IDs from the filtered data
    measurement_ids = measurements_data['id_measurement'].values.tolist()

    # Define the name of the relational table that connects datasets and measurements
    relational_table_name = 'dataset_measurements'

    # Loop through each measurement ID to create the relationship with the dataset
    for measurement_id in measurement_ids:
        # Prepare parameters for the relationship entry
        relational_parameters = {'dataset_id': row_id, 'measurement_id': measurement_id}

        try:
            # Insert the relationship into the relational table
            load_table(cursor, relational_table_name, relational_parameters)
        except Exception as e:
            print(f"Error loading dataset-measurement relationship: {e}")
            conn.rollback()
            cursor.close()
            return
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()

def load_registration(conn,transformation_matrix, reference_file_path, registered_file_path):
    """
    Load a registration into the database, including its metadata.
    
    Parameters:
    -----------
    conn : psycopg2.connection
        Database connection object.
    transformation_matrix : list
        Transformation matrix used for registration.
    reference_file_path : str
        The file path of the reference measurement.
    registered_file_path : str
        The file path of the registered measurement.
        
    Returns:
    --------
    None
        This function doesn't return a value, but prints success or error messages.
        
    Raises:
    -------
    AssertionError
        If any of the input parameters don't meet the expected types/values.
    """
    # Validate input parameters
    assert isinstance(transformation_matrix, list) and len(transformation_matrix) == 3, "Transformation matrix must be a list of 3 lists"
    assert all(isinstance(row, list) and len(row) == 3 for row in transformation_matrix), "Each row of the transformation matrix must be a list of 3 numeric values"
    assert all(isinstance(value, (float, int)) for row in transformation_matrix for value in row), "All values in the transformation matrix must be numeric"
    assert isinstance(reference_file_path, str) and reference_file_path, "Reference file path must be a non-empty string"
    assert isinstance(registered_file_path, str) and registered_file_path, "Registered file path must be a non-empty string"
    
    # Create a cursor object and start a transaction
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction

    # Insert sample names into the xct_measurement_samples table
    measurements_data = dbt.get_data_metadata('measurements')

    measurement_paths = [reference_file_path, registered_file_path]

    # Filter measurements to only include those whose file paths match the provided paths
    measurements_data = measurements_data[measurements_data['file_path_measurement'].isin(measurement_paths)]

    # Extract the measurement IDs from the filtered data
    reference_measurement_id = measurements_data[measurements_data['file_path_measurement'] == reference_file_path]['id_measurement'].values[0]
    registered_measurement_id = measurements_data[measurements_data['file_path_measurement'] == registered_file_path]['id_measurement'].values[0]
    
    # Create the parameters dictionary for registration insertion
    parameters = {
        'transformation_matrix': str(transformation_matrix),
        'reference_measurement_id': reference_measurement_id,
        'registered_measurement_id': registered_measurement_id
    }

    # Load the registration into the database
    table_name = 'registrations'
    try:
        row_id = load_table(cursor, table_name, parameters)
    except Exception as e:
        print(f"Error loading registration: {e}")
        conn.rollback()
        cursor.close()
        return
    
    print(f"Registration loaded with ID: {row_id}")
    
    # Commit the transaction if everything is successful
    conn.commit()
    
    # Close the cursor
    cursor.close()



