import dbtools as dbt

def delete(conn,table_name,ids):
    """
    Deletes rows from a specified table in the database based on a list of IDs.

    Parameters:
    conn (object): Database connection object.
    table_name (str): Name of the table from which to delete rows.
    ids (list): List of IDs of the rows to be deleted.

    Returns:
    None
    """
    if len(ids) == 0:
        return
    
    #convert ids to int
    ids = [int(i) for i in ids]
    
    cursor = conn.cursor()
    conn.autocommit = False  # Start transaction

    placeholders = ', '.join(['%s'] * len(ids))
    query = f"DELETE FROM {table_name} WHERE id IN ({placeholders})"

    try:
        cursor.execute(query, ids)
    except Exception as e:
        conn.rollback()  # Rollback transaction on error
        print(f"Error occurred: {e}")
    finally:
        print(f"Deleted {cursor.rowcount} rows from {table_name} where id is in {ids}")
        conn.commit()
        cursor.close()
