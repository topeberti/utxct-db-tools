# Materials Database Web Interface

This Flask web application provides a user-friendly interface to manage the SQL database for materials, panels, samples, and measurements.

## Features

- Web forms for adding materials, panels, samples, and UT measurements
- View all items in the database
- Automatic file property extraction for UT measurements
- Input validation and error handling
- Clean and responsive user interface

## Setup Instructions

1. Install the required dependencies:

```bash
cd server
pip install -r requirements.txt
```

2. Run the Flask application:

```bash
python app.py
```

3. Open your web browser and navigate to:

```
http://localhost:5000
```

## Usage

### Adding a Material

1. Fill in the "Material Name" field with a descriptive name
2. Enter the "Layer Thickness" value (in mm)
3. Specify the "Layer Layout" as a comma-separated list of angles (e.g., 90, 45, -45, 90)
4. Click "Save Material" to add the material to the database

### Adding a Panel

1. Provide a name for the panel
2. Select the material from the dropdown list
3. Enter the dimensions (height, width, thickness)
4. Specify if the edges are cutted
5. Optionally add a description
6. Click "Save Panel" to add the panel to the database

### Adding a Sample

1. Provide a name for the sample
2. Select the panel from the dropdown list
3. Enter the dimensions (height, width, thickness)
4. Specify if the sample has keyholes and parallel faces
5. Optionally add a description
6. Click "Save Sample" to add the sample to the database

### Adding a UT Measurement

1. Enter the file path to the measurement file
2. Click "Load File Information" to automatically extract file properties
3. Select the measurement type
4. Verify the automatically extracted file properties
5. Specify the signal type and axes order
6. Select the associated samples
7. Optionally provide a parent measurement path and transformations
8. Click "Save UT Measurement" to add the measurement to the database

### Viewing Data

Click on the "View All" links for each data type to see tables of all items in the database.

## Technical Details

- The application uses Flask for the web interface
- Database interactions are handled through the existing `dbtools` module
- Automatic file property extraction uses tifffile to read TIFF files
- AJAX requests are used to get file information without reloading the page
