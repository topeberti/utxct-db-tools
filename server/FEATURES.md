# UTvsXCT Database Web App: Functionality

The app in `server/` is a Flask web interface for the PostgreSQL database that links
ultrasound (UT) and X-ray CT (XCT) measurements to the materials, panels and samples
they were taken from. It is a thin layer over the `dbtools` package: all reads go through
`dbtools.dbtools` and all writes through `dbtools.load` and `dbtools.delete`.

For setup and run instructions see [README.md](README.md). Database credentials come from
the `.env` file used by `dbt.load_credentials` (template: `env_example.txt`).

## Pages at a glance

| Area | Form page | What it stores |
|------|-----------|----------------|
| Main menu | `/` | Links to every form and table view |
| Materials | `/materials` | Material name, layer thickness, extra metadata |
| Fabrication methods | `/fabrication` | Fabrication method name, extra metadata |
| Panels | `/panels` | Panel linked to a material and optional fabrication method, with dimensions, layer layout, description |
| Samples | `/samples` | Sample cut from a panel, with dimensions, keyhole and parallel-faces flags, description |
| Measurement types | `/measurementtype` | Name of a kind of measurement, extra metadata |
| UT measurements | `/ut_measurements` | UT file linked to one or more samples |
| XCT measurements | `/xct_measurements` | XCT file linked to one or more samples |

## Data entry forms

All forms validate their input on the server and report the result as a flash message
(green for success, red for error). A failed submit loads nothing.

### Common behaviour
- **Required fields and numeric checks.** Names must not be empty. Dimensions must be
  positive numbers.
- **Dropdowns from the database.** Panels list existing materials and fabrications.
  Samples list existing panels. Measurements list measurement types and samples.
- **Free-form metadata.** Each form has an "additional metadata" section where you add
  key / value / type rows. They are stored in the matching `*_metadata` table.
- **Suggested metadata fields.** Keys already used in a metadata table are pre-created as
  grey, read-only rows (`templates/_common_metadata.html`) so that the same key is spelled
  the same way every time. Rows left blank are not sent. Keys that the form already has a
  dedicated field for (e.g. height, width, thickness) are not suggested again.

### Measurements
- **Automatic file properties.** After you enter a file path, **Load File Information**
  calls `POST /get_file_info`. The server reads the TIFF (or TIFF folder) with
  `preprocess_tools.io.load_tif` and fills in height, width, depth, data type and file type.
  You can correct the values before saving.
- **Sample links.** A measurement can be linked to several samples. The links are stored in
  `sample_measurements`.
- **Optional fields.** Parent measurement path, signal type, axes order, transformations.
  Transformations are required when a parent measurement path is given.
- **Onlypores and registrations.** The web forms do not load these. Use `load_onlypores`
  and `load_registration` in `dbtools/load.py`. Deleting a measurement in the app also
  removes its onlypores and registrations.

## Table views

Every table has an interactive view under `/view_table/<table_name>`, with one tab per table:
Materials, Fabrications, Panels, Samples, Measurement Types, and Measurements.

- **Readable foreign keys.** Id columns are shown next to the name they point to (for
  example `material_id` next to `material_name`).
- **Column order.** `id`, name or file path, foreign keys, other base columns, then the
  metadata columns in alphabetical order.
- **Table controls.** Search/filter, column show/hide, and paging (see the controls bar in
  `templates/view_table_interactive.html`).
- **Row details.** Click a row to expand every field of that row. Each non-empty value has a
  **Copy** button.
- **Measurements tab.** `/view_relational_table/measurements/samples/sample_measurements`
  shows one row per measurement with its sample names in a `samples` column and their count
  in `n_samples`.

## Deleting rows

Rows can be deleted from the six table views. Deleting is permanent and uses two
confirmation steps.

1. Expand a row and click **Delete row**.
2. **Step 1, review.** A dialog shows what the delete will also remove (linked metadata
   rows, sample links, onlypores and registrations) and the number of rows in each table.
3. **Step 2, confirm.** Type the row's name exactly (the file path for measurements).
   **Delete permanently** stays disabled until the text matches.
4. The result appears as a flash message and the view reloads.

Safeguards:
- **The server checks the typed text again**, so a stray request cannot delete a row.
- **Blocked deletes.** If other rows still reference the row, the dialog lists them and has
  no delete button. These are: panels that use a material or fabrication, samples in a
  panel, measurements of a type, and child measurements of a measurement. Delete those first.
- **Database errors.** A foreign-key violation rolls back the transaction and shows an
  error. Nothing is removed.
- **Cancel.** Cancel, `Esc`, or a click outside the dialog closes it without deleting.

Routes: `GET /delete_preview/<table>/<id>` (JSON summary) and
`POST /delete_row/<table>/<id>` (performs the delete).

## Limitations

- No login and no CSRF protection, and the server listens on `0.0.0.0:5000`. Anyone who can
  reach the server can add and delete data. Run it only on a trusted network.
- The secret key in `app.py` is a placeholder.
- Datasets, experiments and registrations exist in the schema but have no forms or views in
  the web app. Use the `dbtools.load` functions for those.
- No edit function: to change a row, delete it and add it again.
- No automated tests.
