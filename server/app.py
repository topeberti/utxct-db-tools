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

@app.route('/')
def index():
    """Render the main menu page."""
    return render_template('main.html')

@app.route('/materials')
def materials_page():
    """Render the materials form page."""
    return render_template('index.html')

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
    """View all materials in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get materials
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
        
        cursor.close()
        return render_template('view_materials.html', materials=formatted_materials)
        
    except Exception as e:
        flash(f'Error fetching materials: {str(e)}', 'error')
        return redirect(url_for('materials_page'))

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
        return render_template('panel.html', materials=formatted_materials, fabrications=formatted_fabrications)
    
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
        
        # Get edges_cutted (checkbox)
        edges_cutted = request.form.get('edges_cutted') == 'true'
        
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
            result = load.load_panel(conn, name, material_id, fabrication_id, height, width, thickness, edges_cutted, layer_layout, description, additional_metadata)

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
    """View all panels in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get panels with material names
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
        return render_template('view_panels.html', panels=formatted_panels)
        
    except Exception as e:
        flash(f'Error fetching panels: {str(e)}', 'error')
        return redirect(url_for('panels_page'))

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
        return render_template('sample.html', panels=formatted_panels)
    
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

@app.route('/view_samples')
def view_samples():
    """View all samples in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get samples with panel names
        cursor.execute("""
            SELECT s.id, s.name, p.id as panel_id, p.name as panel_name 
            FROM samples s
            JOIN panels p ON s.panel_id = p.id
        """)
        samples = cursor.fetchall()
        
        # Format samples as list of dictionaries
        formatted_samples = []
        for sample in samples:
            sample_id, name, panel_id, panel_name = sample
            
            # Query metadata for this sample
            cursor.execute(
                "SELECT key, value, type FROM sample_metadata WHERE sample_id = %s",
                (sample_id,)
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
            
            # Add sample with its metadata to the list
            formatted_samples.append({
                'id': sample_id,
                'name': name,
                'panel_id': panel_id,
                'panel_name': panel_name,
                'metadata': formatted_metadata
            })
        
        cursor.close()
        return render_template('view_samples.html', samples=formatted_samples)
        
    except Exception as e:
        flash(f'Error fetching samples: {str(e)}', 'error')
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
                              samples=formatted_samples)
    
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
    """View all UT measurements in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get measurements with their measurement types
        cursor.execute("""
            SELECT m.id, m.file_path, m.parent_measurement_id, mt.id as measurementtype_id, mt.name as measurementtype_name 
            FROM measurements m
            JOIN measurementtypes mt ON m.measurementtype_id = mt.id
        """)
        measurements = cursor.fetchall()
        
        # Format measurements as list of dictionaries
        formatted_measurements = []
        for measurement in measurements:
            measurement_id, file_path, parent_measurement_id, measurementtype_id, measurementtype_name = measurement
            
            # Query metadata for this measurement
            cursor.execute(
                "SELECT key, value, type FROM measurement_metadata WHERE measurement_id = %s",
                (measurement_id,)
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
            
            # Get associated samples
            cursor.execute("""
                SELECT s.id, s.name 
                FROM samples s
                JOIN sample_measurements sm ON s.id = sm.sample_id
                WHERE sm.measurement_id = %s
            """, (measurement_id,))
            samples = cursor.fetchall()
            
            # Format samples as list of dictionaries
            formatted_samples = []
            for sample in samples:
                sample_id, sample_name = sample
                formatted_samples.append({
                    'id': sample_id,
                    'name': sample_name
                })
            
            # Add measurement with its metadata and samples to the list
            formatted_measurements.append({
                'id': measurement_id,
                'file_path': file_path,
                'parent_measurement_id': parent_measurement_id,
                'measurementtype_id': measurementtype_id,
                'measurementtype_name': measurementtype_name,
                'metadata': formatted_metadata,
                'samples': formatted_samples
            })
        
        cursor.close()
        return render_template('view_ut_measurements.html', measurements=formatted_measurements)
        
    except Exception as e:
        flash(f'Error fetching UT measurements: {str(e)}', 'error')
        return redirect(url_for('ut_measurements_page'))

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
                              samples=formatted_samples)
    
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
    """View all XCT measurements in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get measurements with their measurement types
        cursor.execute("""
            SELECT m.id, m.file_path, m.parent_measurement_id, mt.id as measurementtype_id, mt.name as measurementtype_name 
            FROM measurements m
            JOIN measurementtypes mt ON m.measurementtype_id = mt.id
            WHERE mt.name LIKE '%XCT%' OR mt.name LIKE '%X-ray%'
        """)
        measurements = cursor.fetchall()
        
        # Format measurements as list of dictionaries
        formatted_measurements = []
        for measurement in measurements:
            measurement_id, file_path, parent_measurement_id, measurementtype_id, measurementtype_name = measurement
            
            # Query metadata for this measurement
            cursor.execute(
                "SELECT key, value, type FROM measurement_metadata WHERE measurement_id = %s",
                (measurement_id,)
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
            
            # Get associated samples
            cursor.execute("""
                SELECT s.id, s.name 
                FROM samples s
                JOIN sample_measurements sm ON s.id = sm.sample_id
                WHERE sm.measurement_id = %s
            """, (measurement_id,))
            samples = cursor.fetchall()
            
            # Format samples as list of dictionaries
            formatted_samples = []
            for sample in samples:
                sample_id, sample_name = sample
                formatted_samples.append({
                    'id': sample_id,
                    'name': sample_name
                })
            
            # Add measurement with its metadata and samples to the list
            formatted_measurements.append({
                'id': measurement_id,
                'file_path': file_path,
                'parent_measurement_id': parent_measurement_id,
                'measurementtype_id': measurementtype_id,
                'measurementtype_name': measurementtype_name,
                'metadata': formatted_metadata,
                'samples': formatted_samples
            })
        
        cursor.close()
        return render_template('view_xct_measurements.html', measurements=formatted_measurements)
        
    except Exception as e:
        flash(f'Error fetching XCT measurements: {str(e)}', 'error')
        return redirect(url_for('xct_measurements_page'))

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
    return render_template('fabrication.html')

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
    """View all fabrication methods in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get fabrication methods
        cursor.execute("SELECT id, name FROM fabrications")
        fabrications = cursor.fetchall()
        
        # Format fabrications as list of dictionaries
        formatted_fabrications = []
        for fabrication in fabrications:
            fabrication_id, name = fabrication
            
            # Query metadata for this fabrication
            cursor.execute(
                "SELECT key, value, type FROM fabrication_metadata WHERE fabrication_id = %s",
                (fabrication_id,)
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
            
            # Add fabrication with its metadata to the list
            formatted_fabrications.append({
                'id': fabrication_id,
                'name': name,
                'metadata': formatted_metadata
            })
        
        cursor.close()
        return render_template('view_fabrications.html', fabrications=formatted_fabrications)
        
    except Exception as e:
        flash(f'Error fetching fabrication methods: {str(e)}', 'error')
        return redirect(url_for('fabrication_page'))

@app.route('/measurementtype')
def measurementtype_page():
    """Render the measurement type form page."""
    return render_template('measurementtype.html')

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

@app.route('/view_measurementtypes')
def view_measurementtypes():
    """View all measurement types in the database."""
    try:
        global conn
        if conn is None or conn.closed:
            conn = dbt.connect()
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Execute query to get measurement types
        cursor.execute("SELECT id, name FROM measurementtypes")
        measurementtypes = cursor.fetchall()
        
        # Format measurement types as list of dictionaries
        formatted_measurementtypes = []
        for measurementtype in measurementtypes:
            measurementtype_id, name = measurementtype
            
            # Query metadata for this measurement type
            cursor.execute(
                "SELECT key, value, type FROM measurementtype_metadata WHERE measurementtype_id = %s",
                (measurementtype_id,)
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
            
            # Add measurement type with its metadata to the list
            formatted_measurementtypes.append({
                'id': measurementtype_id,
                'name': name,
                'metadata': formatted_metadata
            })
        
        cursor.close()
        return render_template('view_measurementtypes.html', measurementtypes=formatted_measurementtypes)
        
    except Exception as e:
        flash(f'Error fetching measurement types: {str(e)}', 'error')
        return redirect(url_for('measurementtype_page'))

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection when the application context ends."""
    global conn
    if conn is not None and not conn.closed:
        conn.close()
        conn = None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
