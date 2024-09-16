from src.config.connectors import get_postgres_conn

def execute_query(query, params=None):
    """
    Execute a query (INSERT, UPDATE, DELETE, etc.) with optional parameters.
    
    :param query: The SQL query to execute.
    :param params: Optional parameters for parameterized queries.
    """
    conn = None
    cursor = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {repr(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_query(query, params=None):
    """
    Execute a SELECT query and fetch results.
    
    :param query: The SQL SELECT query to execute.
    :param params: Optional parameters for parameterized queries.
    :return: List of results from the query.
    """
    conn = None
    cursor = None
    results = []
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {repr(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return results

def copy_from_buffer(buffer, table_name, sep='\t', null_value=None):
    """
    Perform a bulk insert using the PostgreSQL COPY FROM command.
    
    :param buffer: The buffer containing the data to insert.
    :param table_name: The name of the target table.
    :param sep: The delimiter used in the COPY command (default is tab).
    :param null_value: How to represent NULL values in the table (default is None).
    """
    conn = None
    cursor = None
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        cursor.copy_from(buffer, table_name, sep=sep, null=null_value)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred during COPY FROM: {repr(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()