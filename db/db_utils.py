import sqlite3
import pandas as pd

def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.

    Parameters:
    -----------
    db_path : str, optional
        Path to the SQLite database file.

    Returns:
    --------
    sqlite3.Connection
        A connection object to interact with the SQLite database.

    Raises:
    -------
    sqlite3.Error
        If the connection to the database fails.
    """

    conn = sqlite3.connect(db_path)
    return conn



def initialize_db(db_path: str, schema_path: str) -> None:
    """
    Initialize the database by creating all tables and schema objects.

    This function reads the SQL commands from the specified schema file and
    executes them on the database at the given path. It uses `CREATE TABLE IF NOT EXISTS`
    statements (or similar) to create tables, ensuring existing tables are not overwritten.

    Parameters:
    -----------
    db_path : str, optional
        Path to the SQLite database file.
    schema_path : str, optional
        Path to the SQL schema file.

    Returns:
    --------
    None
    """

    conn = get_connection(db_path)
    cursor = conn.cursor()
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())  # uses CREATE TABLE IF NOT EXISTS
    conn.commit()
    conn.close()




def insert_dataframe_to_table(df: pd.DataFrame, db_path: str, table_name: str, if_exists: str = "append") -> None:
    """
    Insert a pandas DataFrame into a SQL database table.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be inserted.
    db_path: str
        The path to the database.
    table_name : str
        The name of the target SQL table.
    if_exists : str, optional, default "append"
        Behavior when the table already exists:
        - 'fail': Raise a ValueError.
        - 'replace': Drop the table before inserting new values.
        - 'append': Insert new values to the existing table.

    Returns:
    --------
    None
        This function performs the insert operation and closes the connection,
        it does not return any value.

    Notes:
    ------
    - This function obtains a database connection via `get_connection()`.
    - The DataFrame index is not written to the database.
    - The connection is closed automatically after insertion.
    """

    conn = get_connection(db_path)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()



def read_table_to_dataframe(db_path: str, table_name: str) -> pd.DataFrame:
    """
    Read data from a SQL table into a pandas DataFrame.

    Parameters:
    -----------
    db_path : str
        The path to the database.
    table_name : str
        The name of the SQL table to read from.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the data from the SQL table.

    Notes:
    ------
    - This function obtains a database connection via `get_connection()`.
    - The connection is closed automatically after the data is read.
    """

    conn = get_connection(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df




# def merge_dataframe_to_table(df: pd.DataFrame, db_connection: sqlite3.Connection, table_name: str, key_columns: list) -> None:
#     """
#     Merge a DataFrame into a SQL table by inserting only new rows (based on key columns).

#     Parameters:
#     -----------
#     df : pd.DataFrame
#         The DataFrame with new data.
#     db_path : str
#         Path to SQLite database file.
#     table_name : str
#         Name of the target SQL table.
#     key_columns : list of str
#         List of columns that uniquely identify a row (natural or surrogate keys).

#     Returns:
#     --------
#     None
#     """

#     existing_df = pd.read_sql_query(f"SELECT * FROM {table_name}", db_connection)

#     # Remove records from df that already exist in table based on key columns
#     if not existing_df.empty:
#         df_to_insert = df.merge(existing_df[key_columns], on=key_columns, how='left', indicator=True)
#         df_to_insert = df_to_insert[df_to_insert['_merge'] == 'left_only']
#         df_to_insert = df_to_insert.drop(columns=['_merge'])
#     else:
#         df_to_insert = df

#     if not df_to_insert.empty:
#         df_to_insert.to_sql(table_name, db_connection, if_exists='append', index=False)



def get_table_schema(connection: sqlite3.Connection, table_name: str) -> dict:
    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    return {
        row[1]: row[2].upper()  # col_name: data_type
        for row in cursor.fetchall()
    }

def enforce_schema_types(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    for col, dtype in schema.items():
        if col not in df.columns:
            df[col] = None
        elif dtype == "INTEGER":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif dtype == "REAL":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif dtype == "TEXT":
            df[col] = df[col].astype(str)
        elif dtype == "BLOB":
            pass
    return df.where(pd.notnull(df), None)  # nahradí NaN za None

def merge_dataframe_to_table(df: pd.DataFrame, db_connection: sqlite3.Connection, table_name: str, key_columns: list) -> None:
    schema = get_table_schema(db_connection, table_name)
    df = enforce_schema_types(df, schema)

    cursor = db_connection.cursor()

    for _, row in df.iterrows():
        # Check if row exists
        where_clause = " AND ".join([f"{col} = ?" for col in key_columns])
        check_query = f"SELECT 1 FROM {table_name} WHERE {where_clause} LIMIT 1"
        key_values = [row[col] for col in key_columns]
        exists = cursor.execute(check_query, key_values).fetchone()

        if exists:
            # UPDATE
            update_cols = [col for col in df.columns if col not in key_columns]
            set_clause = ", ".join([f"{col} = ?" for col in update_cols])
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            update_values = [row[col] for col in update_cols] + key_values
            cursor.execute(update_query, update_values)
        else:
            # INSERT
            col_names = ", ".join(df.columns)
            placeholders = ", ".join(["?"] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
            insert_values = [row[col] for col in df.columns]
            cursor.execute(insert_query, insert_values)

    db_connection.commit()