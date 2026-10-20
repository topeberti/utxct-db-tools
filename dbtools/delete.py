def delete(conn, table_name, ids):
    """
    Deletes rows from a specified table in the database based on a list of IDs.

    The delete runs in one transaction: it is committed on success and rolled back,
    with the exception re-raised, on error (e.g. a foreign key violation).

    Parameters:
    conn (object): Database connection object.
    table_name (str): Name of the table from which to delete rows. Must be a trusted value.
    ids (list): List of IDs of the rows to be deleted.

    Returns:
    int: Number of rows deleted.
    """
    if len(ids) == 0:
        return 0

    #convert ids to int
    ids = [int(i) for i in ids]

    conn.autocommit = False  # Start transaction
    cursor = conn.cursor()
    query = f"DELETE FROM {table_name} WHERE id = ANY(%s)"

    try:
        cursor.execute(query, (ids,))
        deleted = cursor.rowcount
        conn.commit()
    except Exception:
        conn.rollback()  # Rollback transaction on error
        raise
    finally:
        cursor.close()

    print(f"Deleted {deleted} rows from {table_name} where id is in {ids}")
    return deleted
