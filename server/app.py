"""
Flask Web Application for Materials Database

This module provides a web interface to the database loading functions.
It allows users to add materials, panels, samples, and measurements to the database.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sys
import os
import numpy as np
from pathlib import Path
from preprocess_tools import io

# Add the parent directory to the path to import dbtools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dbtools.dbtools as dbt
import dbtools.load as load

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Global connection object
conn = None

# Keys the load functions write from dedicated form fields (not offered as free metadata rows)
_MEASUREMENT_FIXED_KEYS = ('height', 'width', 'depth', 'dtype', 'file_type', 'signal_type',
                           'aligned', 'equalized', 'axes_order', 'transformations')


def _common_metadata(table, exclude=(), marker_key=None):
    """(key, type) pairs used at least twice in a metadata table, most used first.

    `table` must be a hard-coded metadata table name. `marker_key` restricts measurement_metadata
    to measurements that have that key (signal_type -> UT, aligned -> XCT).
    """
    global conn
    try:
        if conn is None or conn.closed:
            conn = dbt.connect()
        params = [list(exclude)]
        marker_filter = ''
        if marker_key:
            marker_filter = ("AND measurement_id IN "
                             "(SELECT measurement_id FROM measurement_metadata WHERE key = %s)")
            params.append(marker_key)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT key, type FROM {table} "
            f"WHERE key <> ALL(%s) AND type IS NOT NULL AND type <> '' {marker_filter} "
            "GROUP BY key, type HAVING COUNT(*) >= 2 "
            "ORDER BY COUNT(*) DESC, key",
            params
        )
        rows = cursor.fetchall()
        cursor.close()
        return [{'key': key, 'type': meta_type} for key, meta_type in rows]
    except Exception:
        if conn is not None and not conn.closed:
            conn.rollback()
        return []

@app.route('/')
def index():
    """Render the main menu page."""
    return render_template('main.html')

@app.route('/materials')
def materials_page():
    """Render the materials form page."""
    return render_template('materials.html',
                           common_metadata=_common_metadata('material_metadata', ('layer_thickness',)))

@app.route('/materials/submit', methods=['GET', 'POST'])
def materials_submit():
    """Handle the material form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        # Validate material name
        if not name or not name.strip():
            flash('Material name is required.', 'error')
            return redirect(url_for('materials_page'))
        
        # Validate and convert layer_thickness to float
        try:
            layer_thickness = float(request.form.get('layer_thickness'))
            if layer_thickness <= 0:
                raise ValueError("Layer thickness must be positive")
        except ValueError as e:
            flash('Layer thickness must be a valid positive number.', 'error')
            return redirect(url_for('materials_page'))
        
        # Parse additional metadata if provided
        additional_metadata = None
        metadata_keys = request.form.getlist('metadata_key[]')
        metadata_values = request.form.getlist('metadata_value[]')
        metadata_types = request.form.getlist('metadata_type[]')
        
        # Process metadata if any fields are provided
        if metadata_keys and any(key.strip() for key in metadata_keys):
            additional_metadata = []
            
            # Validate that all metadata entries have complete information
            for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                key = key.strip()
                value = value.strip()
                meta_type = meta_type.strip()
                
                # Skip empty entries
                if not key and not value and not meta_type:
                    continue
                
                # Validate that all fields are filled for non-empty entries
                if not key or not value or not meta_type:
                    flash(f'Material property {i+1}: All fields (name, value, type) must be filled.', 'error')
                    return redirect(url_for('materials_page'))
                
                additional_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
        
        # Connect to database and call load_material
        try:
            global conn
            if conn is None or conn.closed:
                conn = dbt.connect()
            
            # Call the load_material function with correct parameters
            result = load.load_material(conn, name, layer_thickness, additional_metadata)

            if result == -1:
                flash(f'Error loading material "{name}".', 'error')
            else:
                flash(f'Material "{name}" successfully added to the database!', 'success')
            return redirect(url_for('materials_page'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('materials_page'))
    
    # GET request - just show the form
    return redirect(url_for('materials_page'))

@app.route('/view_materials')
def view_materials():
    """View all materials in the database using generic interactive table."""
    return redirect(url_for('view_table', table_name='materials'))

@app.route('/panels')
def panels_page():
    """Render the panels form page."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get all materials for the dropdown
        cursor.execute("SELECT id, name FROM materials")
        materials = cursor.fetchall()
        
        # Format materials as list of dictionaries
        formatted_materials = []
        for material in materials:
            material_id, name = material
            
            # Query metadata for this material
            cursor.execute(
                "SELECT key, value, type FROM material_metadata WHERE material_id = %s",
                (material_id,)
            )
            metadata = cursor.fetchall()
            
            # Format metadata as list of dictionaries
            formatted_metadata = []
            for meta in metadata:
                key, value, meta_type = meta
                formatted_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
            
            # Add material with its metadata to the list
            formatted_materials.append({
                'id': material_id,
                'name': name,
                'metadata': formatted_metadata
            })
        
        # Get all fabrication methods for the dropdown
        cursor.execute("SELECT id, name FROM fabrications")
        fabrications = cursor.fetchall()
        
        # Format fabrications as list of dictionaries
        formatted_fabrications = []
        for fabrication in fabrications:
            fabrication_id, name = fabrication
            formatted_fabrications.append({
                'id': fabrication_id,
                'name': name
            })
        
        cursor.close()
        return render_template('panel.html', materials=formatted_materials, fabrications=formatted_fabrications,
                               common_metadata=_common_metadata(
                                   'panel_metadata', ('height', 'width', 'thickness', 'layer_layout')))
    
    except Exception as e:
        flash(f'Error loading data for panel form: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/panels/submit', methods=['GET', 'POST'])
def panels_submit():
    """Handle the panel form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        # Validate panel name
        if not name or not name.strip():
            flash('Panel name is required.', 'error')
            return redirect(url_for('panels_page'))
        
        # Validate and convert material_id to int
        try:
            material_id = int(request.form.get('material_id'))
        except ValueError:
            flash('Please select a valid material.', 'error')
            return redirect(url_for('panels_page'))
        
        # Validate and convert fabrication_id to int
        try:
            fabrication_id = int(request.form.get('fabrication_id'))
        except ValueError:
            flash('Please select a valid fabrication method.', 'error')
            return redirect(url_for('panels_page'))
        
        # Validate and convert dimensions to float
        try:
            height = float(request.form.get('height'))
            width = float(request.form.get('width'))
            thickness = float(request.form.get('thickness'))
            
            if height <= 0 or width <= 0 or thickness <= 0:
                raise ValueError("Dimensions must be positive")
        except ValueError:
            flash('Dimensions must be valid positive numbers.', 'error')
            return redirect(url_for('panels_page'))
        
        # Get optional layer_layout
        layer_layout = None
        layer_layout_str = request.form.get('layer_layout')
        if layer_layout_str and layer_layout_str.strip():
            try:
                # Split by commas and convert to integers
                layer_layout = [int(angle.strip()) for angle in layer_layout_str.split(',')]
                if not layer_layout:
                    raise ValueError("Layer layout cannot be empty if provided")
            except ValueError as e:
                flash(f'Invalid layer layout format: {str(e)}. Please enter comma-separated integers.', 'error')
                return redirect(url_for('panels_page'))
        
        # Get optional description
        description = request.form.get('description') or None
        
        # Parse additional metadata if provided
        additional_metadata = None
        metadata_keys = request.form.getlist('metadata_key[]')
        metadata_values = request.form.getlist('metadata_value[]')
        metadata_types = request.form.getlist('metadata_type[]')
        
        # Process metadata if any fields are provided
        if metadata_keys and any(key.strip() for key in metadata_keys):
            additional_metadata = []
            
            # Validate that all metadata entries have complete information
            for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                key = key.strip()
                value = value.strip()
                meta_type = meta_type.strip()
                
                # Skip empty entries
                if not key and not value and not meta_type:
                    continue
                
                # Validate that all fields are filled for non-empty entries
                if not key or not value or not meta_type:
                    flash(f'Panel property {i+1}: All fields (name, value, type) must be filled.', 'error')
                    return redirect(url_for('panels_page'))
                
                additional_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
        
        # Connect to database and call load_panel
        try:
            global conn
            if conn is None or conn.closed:
                conn = dbt.connect()
            
            # Call the load_panel function with correct parameters
            result = load.load_panel(conn, name, material_id, fabrication_id, height, width, thickness, layer_layout, description, additional_metadata)

            if result == -1:
                flash(f'Error loading panel "{name}".', 'error')
            else:
                flash(f'Panel "{name}" successfully added to the database!', 'success')
            return redirect(url_for('panels_page'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('panels_page'))
    
    # GET request - just show the form
    return redirect(url_for('panels_page'))

@app.route('/view_panels')
def view_panels():
    """View all panels in the database using generic interactive table."""
    return redirect(url_for('view_table', table_name='panels'))

@app.route('/view_samples')
def view_samples():
    """View all samples in the database using generic interactive table."""
    return redirect(url_for('view_table', table_name='samples'))

@app.route('/view_measurementtypes')
def view_measurementtypes():
    """View all measurement types in the database using generic interactive table."""
    return redirect(url_for('view_table', table_name='measurementtypes'))

@app.route('/samples')
def samples_page():
    """Render the samples form page."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get all panels for the dropdown
        cursor.execute("""
            SELECT p.id, p.name, m.id as material_id, m.name as material_name 
            FROM panels p
            JOIN materials m ON p.material_id = m.id
        """)
        panels = cursor.fetchall()
        
        # Format panels as list of dictionaries
        formatted_panels = []
        for panel in panels:
            panel_id, name, material_id, material_name = panel
            
            # Query metadata for this panel
            cursor.execute(
                "SELECT key, value, type FROM panel_metadata WHERE panel_id = %s",
                (panel_id,)
            )
            metadata = cursor.fetchall()
            
            # Format metadata as list of dictionaries
            formatted_metadata = []
            for meta in metadata:
                key, value, meta_type = meta
                formatted_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
            
            # Add panel with its metadata to the list
            formatted_panels.append({
                'id': panel_id,
                'name': name,
                'material_id': material_id,
                'material_name': material_name,
                'metadata': formatted_metadata
            })
        
        cursor.close()
        return render_template('sample.html', panels=formatted_panels,
                               common_metadata=_common_metadata(
                                   'sample_metadata',
                                   ('height', 'width', 'thickness', 'keyhole', 'parallel_faces')))
    
    except Exception as e:
        flash(f'Error loading panels for sample form: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/samples/submit', methods=['GET', 'POST'])
def samples_submit():
    """Handle the sample form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        # Validate sample name
        if not name or not name.strip():
            flash('Sample name is required.', 'error')
            return redirect(url_for('samples_page'))
        
        # Validate and convert panel_id to int
        try:
            panel_id = int(request.form.get('panel_id'))
        except ValueError:
            flash('Please select a valid panel.', 'error')
            return redirect(url_for('samples_page'))
        
        # Validate and convert dimensions to float
        try:
            height = float(request.form.get('height'))
            width = float(request.form.get('width'))
            thickness = float(request.form.get('thickness'))
            
            if height <= 0 or width <= 0 or thickness <= 0:
                raise ValueError("Dimensions must be positive")
        except ValueError:
            flash('Dimensions must be valid positive numbers.', 'error')
            return redirect(url_for('samples_page'))
        
        # Get checkbox values
        keyhole = request.form.get('keyhole') == 'true'
        parallel_faces = request.form.get('parallel_faces') == 'true'
        
        # Get optional description
        description = request.form.get('description') or None
        
        # Parse additional metadata if provided
        additional_metadata = None
        metadata_keys = request.form.getlist('metadata_key[]')
        metadata_values = request.form.getlist('metadata_value[]')
        metadata_types = request.form.getlist('metadata_type[]')
        
        # Process metadata if any fields are provided
        if metadata_keys and any(key.strip() for key in metadata_keys):
            additional_metadata = []
            
            # Validate that all metadata entries have complete information
            for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                key = key.strip()
                value = value.strip()
                meta_type = meta_type.strip()
                
                # Skip empty entries
                if not key and not value and not meta_type:
                    continue
                
                # Validate that all fields are filled for non-empty entries
                if not key or not value or not meta_type:
                    flash(f'Sample property {i+1}: All fields (name, value, type) must be filled.', 'error')
                    return redirect(url_for('samples_page'))
                
                additional_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
        
        # Connect to database and call load_sample
        try:
            global conn
            if conn is None or conn.closed:
                conn = dbt.connect()
            
            # Call the load_sample function with correct parameters
            result = load.load_sample(conn, name, panel_id, height, width, thickness, keyhole, parallel_faces, description, additional_metadata)

            if result == -1:
                flash(f'Error loading sample "{name}".', 'error')
            else:
                flash(f'Sample "{name}" successfully added to the database!', 'success')
            return redirect(url_for('samples_page'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('samples_page'))
    
    # GET request - just show the form
    return redirect(url_for('samples_page'))



@app.route('/ut_measurements')
def ut_measurements_page():
    """Render the UT measurements form page."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get all measurement types
        cursor.execute("SELECT id, name, description FROM measurementtypes")
        measurement_types = cursor.fetchall()
        
        # Format measurement types as list of dictionaries
        formatted_measurement_types = []
        for mtype in measurement_types:
            mtype_id, name, description = mtype
            formatted_measurement_types.append({
                'id': mtype_id,
                'name': name,
                'description': description
            })
        
        # Get all samples for association
        cursor.execute("""
            SELECT s.id, s.name, p.name as panel_name 
            FROM samples s
            JOIN panels p ON s.panel_id = p.id
        """)
        samples = cursor.fetchall()
        
        # Format samples as list of dictionaries
        formatted_samples = []
        for sample in samples:
            sample_id, name, panel_name = sample
            formatted_samples.append({
                'id': sample_id,
                'name': name,
                'panel_name': panel_name
            })
        
        cursor.close()
        return render_template('ut_measurement.html',
                              measurement_types=formatted_measurement_types,
                              samples=formatted_samples,
                              common_metadata=_common_metadata(
                                  'measurement_metadata', _MEASUREMENT_FIXED_KEYS, marker_key='signal_type'))
    
    except Exception as e:
        flash(f'Error loading form data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/ut_measurements/submit', methods=['GET', 'POST'])
def ut_measurements_submit():
    """Handle the UT measurement form submission."""
    if request.method == 'POST':
        try:
            # Get file information
            file_path = request.form.get('file_path')
            parent_measurement_path = request.form.get('parent_measurement_path') or None
            transformations = request.form.get('transformations') or None
            
            # Validate transformations if parent path is provided
            if parent_measurement_path and not transformations:
                flash('Transformations are required when a parent measurement is specified.', 'error')
                return redirect(url_for('ut_measurements_page'))
            
            # Get measurement type
            try:
                measurementtype_id = int(request.form.get('measurementtype_id'))
            except ValueError:
                flash('Please select a valid measurement type.', 'error')
                return redirect(url_for('ut_measurements_page'))
            
            # Get file properties
            try:
                height = int(request.form.get('height'))
                width = int(request.form.get('width'))
                depth = int(request.form.get('depth'))
            except ValueError:
                flash('Dimensions must be valid integers.', 'error')
                return redirect(url_for('ut_measurements_page'))
            
            dtype = request.form.get('dtype')
            file_type = request.form.get('file_type')
            signal_type = request.form.get('signal_type')
            
            # Get axes order
            axes_order = [
                request.form.get('axes_order_1'),
                request.form.get('axes_order_2'),
                request.form.get('axes_order_3')
            ]
            
            # Validate axes order has unique values
            if len(set(axes_order)) != 3:
                flash('Axes order must contain unique values for x, y, and z.', 'error')
                return redirect(url_for('ut_measurements_page'))
            
            # Get sample IDs and convert them to names
            try:
                sample_ids = request.form.getlist('sample_ids')
                if not sample_ids:
                    flash('Please select at least one sample.', 'error')
                    return redirect(url_for('ut_measurements_page'))
                
                # Get sample names from IDs using direct SQL query
                global conn
                if conn is None or conn.closed:
                    conn = dbt.connect()
                
                cursor = conn.cursor()
                
                # Create a tuple of IDs for the SQL query
                ids_str = ','.join([str(id) for id in sample_ids])
                query = f"SELECT name FROM samples WHERE id IN ({ids_str})"
                cursor.execute(query)
                sample_names = [row[0] for row in cursor.fetchall()]
                cursor.close()
                
                # Parse additional metadata if provided
                additional_metadata = None
                metadata_keys = request.form.getlist('metadata_key[]')
                metadata_values = request.form.getlist('metadata_value[]')
                metadata_types = request.form.getlist('metadata_type[]')
                
                # Process metadata if any fields are provided
                if metadata_keys and any(key.strip() for key in metadata_keys):
                    additional_metadata = []
                    
                    # Validate that all metadata entries have complete information
                    for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                        key = key.strip()
                        value = value.strip()
                        meta_type = meta_type.strip()
                        
                        # Skip empty entries
                        if not key and not value and not meta_type:
                            continue
                        
                        # Validate that all fields are filled for non-empty entries
                        if not key or not value or not meta_type:
                            flash(f'Metadata field {i+1}: All fields (key, value, type) must be filled.', 'error')
                            return redirect(url_for('ut_measurements_page'))
                        
                        additional_metadata.append({
                            'key': key,
                            'value': value,
                            'type': meta_type
                        })
                
                # Create a new connection for the load_ut_measurement function
                # This avoids transaction conflicts with get_data_metadata
                new_conn = dbt.connect()
                
                # Call the load_ut_measurement function with the new connection
                result = load.load_ut_measurement(
                    new_conn, file_path, measurementtype_id, 
                    height, width, depth, dtype,
                    file_type, signal_type, axes_order,
                    sample_names, parent_measurement_path, transformations, additional_metadata
                )
                
                # Close the new connection
                new_conn.close()

                if result == -1:
                    flash(f'Error loading UT measurement.', 'error')
                else:
                    flash(f'UT measurement successfully added to the database!', 'success')
                return redirect(url_for('ut_measurements_page'))

            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('ut_measurements_page'))
                
        except Exception as e:
            flash(f'Error processing form: {str(e)}', 'error')
            return redirect(url_for('ut_measurements_page'))
    
    # GET request - just show the form
    return redirect(url_for('ut_measurements_page'))

@app.route('/view_ut_measurements')
def view_ut_measurements():
    """View all UT measurements with their related samples using relational table."""
    return redirect(url_for('view_relational_table', 
                          main_table_name='measurements', 
                          secondary_table_name='samples', 
                          relational_table='sample_measurements'))

@app.route('/xct_measurements')
def xct_measurements_page():
    """Render the XCT measurements form page."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get all measurement types
        cursor.execute("SELECT id, name, description FROM measurementtypes")
        measurement_types = cursor.fetchall()
        
        # Format measurement types as list of dictionaries
        formatted_measurement_types = []
        for mtype in measurement_types:
            mtype_id, name, description = mtype
            formatted_measurement_types.append({
                'id': mtype_id,
                'name': name,
                'description': description
            })
        
        # Get all samples for association
        cursor.execute("""
            SELECT s.id, s.name, p.name as panel_name 
            FROM samples s
            JOIN panels p ON s.panel_id = p.id
        """)
        samples = cursor.fetchall()
        
        # Format samples as list of dictionaries
        formatted_samples = []
        for sample in samples:
            sample_id, name, panel_name = sample
            formatted_samples.append({
                'id': sample_id,
                'name': name,
                'panel_name': panel_name
            })
        
        cursor.close()
        return render_template('xct_measurement.html',
                              measurement_types=formatted_measurement_types,
                              samples=formatted_samples,
                              common_metadata=_common_metadata(
                                  'measurement_metadata', _MEASUREMENT_FIXED_KEYS, marker_key='aligned'))
    
    except Exception as e:
        flash(f'Error loading form data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/xct_measurements/submit', methods=['GET', 'POST'])
def xct_measurements_submit():
    """Handle the XCT measurement form submission."""
    if request.method == 'POST':
        try:
            # Get file information
            file_path = request.form.get('file_path')
            parent_measurement_path = request.form.get('parent_measurement_path') or None
            transformations = request.form.get('transformations') or None
            
            # Validate transformations if parent path is provided
            if parent_measurement_path and not transformations:
                flash('Transformations are required when a parent measurement is specified.', 'error')
                return redirect(url_for('xct_measurements_page'))
            
            # Get measurement type
            try:
                measurementtype_id = int(request.form.get('measurementtype_id'))
            except ValueError:
                flash('Please select a valid measurement type.', 'error')
                return redirect(url_for('xct_measurements_page'))
            
            # Get file properties
            try:
                height = int(request.form.get('height'))
                width = int(request.form.get('width'))
                depth = int(request.form.get('depth'))
            except ValueError:
                flash('Dimensions must be valid integers.', 'error')
                return redirect(url_for('xct_measurements_page'))
            dtype = request.form.get('dtype')
            file_type = request.form.get('file_type')
            
            # Get XCT specific properties
            aligned = request.form.get('aligned') == 'true'
            equalized = request.form.get('equalized') == 'true'
            
            # Get axes order
            axes_order = [
                request.form.get('axes_order_1'),
                request.form.get('axes_order_2'),
                request.form.get('axes_order_3')
            ]
            
            # Validate axes order has unique values
            if len(set(axes_order)) != 3:
                flash('Axes order must contain unique values for x, y, and z.', 'error')
                return redirect(url_for('xct_measurements_page'))
            
            # Get sample IDs and names
            try:
                sample_ids = request.form.getlist('sample_ids')
                if not sample_ids:
                    flash('Please select at least one sample.', 'error')
                    return redirect(url_for('xct_measurements_page'))
                
                # Get sample names from IDs using direct SQL query
                global conn
                if conn is None or conn.closed:
                    conn = dbt.connect()
                
                cursor = conn.cursor()
                
                # Create a tuple of IDs for the SQL query
                ids_str = ','.join([str(id) for id in sample_ids])
                query = f"SELECT name FROM samples WHERE id IN ({ids_str})"
                cursor.execute(query)
                sample_names = [row[0] for row in cursor.fetchall()]
                cursor.close()
                
                # Parse additional metadata if provided
                additional_metadata = None
                metadata_keys = request.form.getlist('metadata_key[]')
                metadata_values = request.form.getlist('metadata_value[]')
                metadata_types = request.form.getlist('metadata_type[]')
                
                # Process metadata if any fields are provided
                if metadata_keys and any(key.strip() for key in metadata_keys):
                    additional_metadata = []
                    
                    # Validate that all metadata entries have complete information
                    for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                        key = key.strip()
                        value = value.strip()
                        meta_type = meta_type.strip()
                        
                        # Skip empty entries
                        if not key and not value and not meta_type:
                            continue
                        
                        # Validate that all fields are filled for non-empty entries
                        if not key or not value or not meta_type:
                            flash(f'Metadata field {i+1}: All fields (key, value, type) must be filled.', 'error')
                            return redirect(url_for('xct_measurements_page'))
                        
                        additional_metadata.append({
                            'key': key,
                            'value': value,
                            'type': meta_type
                        })
                
                # Create a new connection for the load_xct_measurement function
                # This avoids transaction conflicts with get_data_metadata
                new_conn = dbt.connect()
                
                # Call the load_xct_measurement function with the new connection
                result = load.load_xct_measurement(
                    new_conn, file_path, measurementtype_id, 
                    height, width, depth, dtype, file_type,
                    sample_names, aligned, equalized, axes_order,
                    parent_measurement_path, transformations, additional_metadata
                )
                
                # Close the new connection
                new_conn.close()

                if result == -1:
                    flash(f'Error loading XCT measurement.', 'error')
                else:
                    flash(f'XCT measurement successfully added to the database!', 'success')
                return redirect(url_for('xct_measurements_page'))

            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
                return redirect(url_for('xct_measurements_page'))
                
        except Exception as e:
            flash(f'Error processing form: {str(e)}', 'error')
            return redirect(url_for('xct_measurements_page'))
    
    # GET request - just show the form
    return redirect(url_for('xct_measurements_page'))

@app.route('/view_xct_measurements')
def view_xct_measurements():
    """View all XCT measurements with their related samples using relational table."""
    return redirect(url_for('view_relational_table', 
                          main_table_name='measurements', 
                          secondary_table_name='samples', 
                          relational_table='sample_measurements'))

@app.route('/get_file_info', methods=['POST'])
def get_file_info():
    """API endpoint to extract file information from UT measurement files."""
    try:
        # Get file path from request
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Check file extension
        file_type = os.path.splitext(file_path)[1]
        if not file_type:  # If it's a directory of TIFFs
            file_type = 'folder'
        
        # Load file and extract properties
        try:
            from preprocess_tools import io
            
            # Load the file using preprocess_tools.io
            file = io.load_tif(file_path)
            
            # Extract dimensions
            if len(file.shape) == 3:
                height, width, depth = file.shape
            elif len(file.shape) == 2:
                height, width = file.shape
                depth = 1
            else:
                return jsonify({'error': f'Unsupported file shape: {file.shape}'}), 400
            
            # Get data type
            dtype = str(file.dtype)
            
            return jsonify({
                'height': height,
                'width': width,
                'depth': depth,
                'dtype': dtype,
                'file_type': file_type
            })
            
        except ImportError as import_error:
            return jsonify({'error': f'Required module not installed: {str(import_error)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/fabrication')
def fabrication_page():
    """Render the fabrication form page."""
    return render_template('fabrication.html',
                           common_metadata=_common_metadata('fabrication_metadata'))

@app.route('/fabrication/submit', methods=['GET', 'POST'])
def fabrication_submit():
    """Handle the fabrication form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        # Validate fabrication name
        if not name or not name.strip():
            flash('Fabrication method name is required.', 'error')
            return redirect(url_for('fabrication_page'))
        
        # Parse additional metadata if provided
        additional_metadata = None
        metadata_keys = request.form.getlist('metadata_key[]')
        metadata_values = request.form.getlist('metadata_value[]')
        metadata_types = request.form.getlist('metadata_type[]')
        
        # Process metadata if any fields are provided
        if metadata_keys and any(key.strip() for key in metadata_keys):
            additional_metadata = []
            
            # Validate that all metadata entries have complete information
            for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                key = key.strip()
                value = value.strip()
                meta_type = meta_type.strip()
                
                # Skip empty entries
                if not key and not value and not meta_type:
                    continue
                
                # Validate that all fields are filled for non-empty entries
                if not key or not value or not meta_type:
                    flash(f'Metadata entry {i+1}: All fields (key, value, type) must be filled.', 'error')
                    return redirect(url_for('fabrication_page'))
                
                additional_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
        
        # Connect to database and call load_fabrication
        try:
            global conn
            if conn is None or conn.closed:
                conn = dbt.connect()
            
            # Call the load_fabrication function
            result = load.load_fabrication(conn, name, additional_metadata)

            if result == -1:
                flash(f'Error loading fabrication method "{name}".', 'error')
            else:
                flash(f'Fabrication method "{name}" successfully added to the database!', 'success')
            return redirect(url_for('fabrication_page'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('fabrication_page'))
    
    # GET request - just show the form
    return redirect(url_for('fabrication_page'))

@app.route('/view_fabrications')
def view_fabrications():
    """View all fabrication methods in the database using generic interactive table."""
    return redirect(url_for('view_table', table_name='fabrications'))

@app.route('/measurementtype')
def measurementtype_page():
    """Render the measurement type form page."""
    return render_template('measurementtype.html',
                           common_metadata=_common_metadata('measurementtype_metadata'))

@app.route('/measurementtype/submit', methods=['GET', 'POST'])
def measurementtype_submit():
    """Handle the measurement type form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        # Validate measurement type name
        if not name or not name.strip():
            flash('Measurement type name is required.', 'error')
            return redirect(url_for('measurementtype_page'))
        
        # Parse additional metadata if provided
        additional_metadata = None
        metadata_keys = request.form.getlist('metadata_key[]')
        metadata_values = request.form.getlist('metadata_value[]')
        metadata_types = request.form.getlist('metadata_type[]')
        
        # Process metadata if any fields are provided
        if metadata_keys and any(key.strip() for key in metadata_keys):
            additional_metadata = []
            
            # Validate that all metadata entries have complete information
            for i, (key, value, meta_type) in enumerate(zip(metadata_keys, metadata_values, metadata_types)):
                key = key.strip()
                value = value.strip()
                meta_type = meta_type.strip()
                
                # Skip empty entries
                if not key and not value and not meta_type:
                    continue
                
                # Validate that all fields are filled for non-empty entries
                if not key or not value or not meta_type:
                    flash(f'Measurement property {i+1}: All fields (name, value, type) must be filled.', 'error')
                    return redirect(url_for('measurementtype_page'))
                
                additional_metadata.append({
                    'key': key,
                    'value': value,
                    'type': meta_type
                })
        
        # Connect to database and call load_measurementtype
        try:
            global conn
            if conn is None or conn.closed:
                conn = dbt.connect()
            
            # Call the load_measurementtype function
            result = load.load_measurementtype(conn, name, additional_metadata)

            if result == -1:
                flash(f'Error loading measurement type "{name}".', 'error')
            else:
                flash(f'Measurement type "{name}" successfully added to the database!', 'success')
            return redirect(url_for('measurementtype_page'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('measurementtype_page'))
    
    # GET request - just show the form
    return redirect(url_for('measurementtype_page'))


    
# Foreign keys shown by name in the table views: table -> {fk column: (parent table, parent label column)}
_FK_NAMES = {
    'panels': {'material_id': ('materials', 'name'), 'fabrication_id': ('fabrications', 'name')},
    'samples': {'panel_id': ('panels', 'name')},
    'measurements': {'measurementtype_id': ('measurementtypes', 'name'),
                     'parent_measurement_id': ('measurements', 'file_path')},
}

_TABLE_VIEWS = [
    ('materials', 'Materials', 'view_table', {'table_name': 'materials'}),
    ('fabrications', 'Fabrications', 'view_table', {'table_name': 'fabrications'}),
    ('panels', 'Panels', 'view_table', {'table_name': 'panels'}),
    ('samples', 'Samples', 'view_table', {'table_name': 'samples'}),
    ('measurementtypes', 'Measurement Types', 'view_table', {'table_name': 'measurementtypes'}),
    ('measurements_samples', 'Measurements', 'view_relational_table',
     {'main_table_name': 'measurements', 'secondary_table_name': 'samples',
      'relational_table': 'sample_measurements'}),
]


def _table_views():
    """Navigation entries (key, label, url) for all table views."""
    return [(key, label, url_for(endpoint, **kwargs)) for key, label, endpoint, kwargs in _TABLE_VIEWS]


def _clean_table(df, table_name):
    """Strip the table suffix from the columns, add FK name columns and order the columns.

    Order: id, name/file_path, FK columns (id followed by its name), other base columns, then metadata columns.
    """
    suffix = '_' + table_name[:-1]
    df = df.rename(columns=lambda c: c[:-len(suffix)] if c.endswith(suffix) else c)
    base_cols = [c for c in df.columns if c in ('id', 'name', 'file_path', 'description')
                 or c.endswith('_id')]

    for fk_col, (parent, label_col) in _FK_NAMES.get(table_name, {}).items():
        if fk_col not in df.columns:
            continue
        parent_df = dbt.get_data(parent)
        parent_suffix = '_' + parent[:-1]
        labels = dict(zip(parent_df['id' + parent_suffix], parent_df[label_col + parent_suffix]))
        name_col = fk_col[:-3] + '_name' if fk_col != 'parent_measurement_id' else 'parent_measurement'
        df.insert(df.columns.get_loc(fk_col) + 1, name_col, df[fk_col].map(labels))
        base_cols.insert(base_cols.index(fk_col) + 1, name_col)

    # nullable FK columns arrive as float (252.0) when they contain NULLs
    for col in df.columns:
        if col.endswith('_id') and df[col].dtype == float:
            df[col] = df[col].astype('Int64')

    lead = [c for c in ('id', 'name', 'file_path') if c in df.columns]
    rest_base = [c for c in base_cols if c not in lead]
    metadata = sorted(c for c in df.columns if c not in lead and c not in rest_base)
    return df[lead + rest_base + metadata]


def _df_to_table_data(df):
    """Convert a DataFrame to JSON-safe {'columns', 'data'} (NaN/None -> '')."""
    df = df.astype(object).where(df.notna(), '')
    data = [[v.item() if hasattr(v, 'item') else v for v in row] for row in df.values.tolist()]
    return {'columns': [str(c) for c in df.columns], 'data': data}


@app.route('/view_table/<table_name>')
def view_table(table_name):
    """Generic function to view any table in the database using interactive dataframe."""
    try:
        # Validate table name to prevent SQL injection
        valid_tables = ['materials', 'fabrications', 'panels', 'samples', 'measurements', 'measurementtypes']
        if table_name not in valid_tables:
            flash(f'Invalid table name: {table_name}', 'error')
            return redirect(url_for('index'))

        table_df = _clean_table(dbt.get_data_metadata(table_name), table_name)

        return render_template('view_table_interactive.html',
                             table_data=_df_to_table_data(table_df),
                             table_name=table_name,
                             table_title=table_name.replace('_', ' ').title(),
                             views=_table_views(),
                             current_view=table_name)

    except Exception as e:
        flash(f'Error fetching data from {table_name}: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/view_relational_table/<main_table_name>/<secondary_table_name>/<relational_table>')
def view_relational_table(main_table_name, secondary_table_name, relational_table):
    """View measurements with their linked samples collapsed into one row per measurement.

    Only the measurements/samples/sample_measurements combination is supported. The sample names of
    each measurement go in the 'samples' column (comma-separated) and their count in 'n_samples'.
    """
    try:
        # Validate table names to prevent SQL injection
        if (main_table_name, secondary_table_name, relational_table) != ('measurements', 'samples', 'sample_measurements'):
            flash(f'Invalid table combination: {main_table_name}, {secondary_table_name}, {relational_table}', 'error')
            return redirect(url_for('index'))

        table_df = _clean_table(dbt.get_data_metadata('measurements'), 'measurements')

        links = dbt.get_data('sample_measurements')
        sample_names = dbt.get_data('samples').set_index('id_sample')['name_sample']
        grouped = {}
        if not links.empty:
            links = links.assign(sample_name=links['sample_id_sample_measurement'].map(sample_names))
            for measurement_id, names in links.groupby('measurement_id_sample_measurement')['sample_name']:
                grouped[measurement_id] = sorted(str(n) for n in names)

        table_df['samples'] = table_df['id'].map(lambda i: ', '.join(grouped.get(i, [])))
        table_df['n_samples'] = table_df['id'].map(lambda i: len(grouped.get(i, [])))

        return render_template('view_table_interactive.html',
                             table_data=_df_to_table_data(table_df),
                             table_name='measurements_samples',
                             table_title='Measurements with Related Samples',
                             views=_table_views(),
                             current_view='measurements_samples')

    except Exception as e:
        flash(f'Error fetching data from {main_table_name} and {secondary_table_name}: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection when the application context ends."""
    global conn
    if conn is not None and not conn.closed:
        conn.close()
        conn = None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
