import io
from src.services.db_utils import copy_from_buffer, execute_query
from src.services.checkpoint import CheckpointManager

class Ingestor:
    def __init__(self, target_table_name, staging_table_name, column_definitions, conflict_columns, update_columns):
        """
        Initialize the TableIngestion class with relevant parameters.

        :param target_table_name: The name of the target table.
        :param staging_table_name: The name of the staging table.
        :param column_definitions: A dictionary defining the column names and types.
        :param conflict_columns: List of columns to check for conflicts (e.g., ['station_id', 'date']).
        :param update_columns: List of columns to update if a conflict occurs.
        """
        self.target_table_name = target_table_name
        self.staging_table_name = staging_table_name
        self.column_definitions = column_definitions
        self.conflict_columns = conflict_columns
        self.update_columns = update_columns
        self.checkpoint_manager = CheckpointManager()

    def insert_into_staging(self, df, sep='\t', null_value=None):
        """
        Insert data into the staging table dynamically using COPY.

        Reason for Staging Table: Since we do not want records to be added twice, we need a way to handle conflicts. While at the moment we can efficiently
        handle conflicts using ON CONFLICT, it might still become very slow down the line if more and more conflicts arise in insertion stage. To handle this, 
        we will input data into a staging table as is, from where we will merge it into the final table where postgres itself will handle conflict resolution 
        in bulk. This would make the entire ingestion process much smoother and faster.

        Reason for COPY: Generally faster than INSERT INTO, reduced chances of LOCKING issues, does batch insertion among a ton of other benefits. It's just better ngl.

        :param df: The DataFrame containing the data to insert.
        :param staging_table_name: The name of the staging table.
        :param column_definitions: A dictionary defining the column names and types. e.g. {'station_id': 'VARCHAR', 'date': 'DATE', ...}.
        :param sep: The delimiter used in the COPY command (default is tab).
        :param null_value: How to represent NULL values in the table (default is None).
        """

        # Creates staging table if doesn't exist
        column_def_str = ', '.join([f"{col} {dtype}" for col, dtype in self.column_definitions.items()])
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.staging_table_name} (
            {column_def_str},
            PRIMARY KEY ({', '.join([k for k, v in self.column_definitions.items() if v in ['VARCHAR', 'DATE']] )})
        );
        """
        execute_query(create_table_query)

        # Does copy_from_buffer to insert data into staging table
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False, sep=sep)
        buffer.seek(0)
        copy_from_buffer(buffer, self.staging_table_name, sep=sep, null_value=null_value)

    def upsert_from_staging(self):
        """
        Perform the upsert from the staging table into the target table.
        """

        # Builds the conflict clause and update clause dynamically
        conflict_clause = ', '.join(self.conflict_columns)
        update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in self.update_columns])

        # Performs the upsert from the staging table to the target table
        upsert_query = f"""
        INSERT INTO {self.target_table_name} ({', '.join(self.conflict_columns + self.update_columns)})
        SELECT {', '.join(self.conflict_columns + self.update_columns)} FROM {self.staging_table_name}
        ON CONFLICT ({conflict_clause})
        DO UPDATE SET {update_clause};
        """
        execute_query(upsert_query)

    def delete_staging_table(self):
        # Deletes staging table after completion of process... probably could be a standalone function that could delete any table.
        drop_table_query = f"DROP TABLE IF EXISTS {self.staging_table_name};"
        execute_query(drop_table_query)

    def ingest_table(self, file_name, df, sep='\t', null_value=None):
        """
        Perform the entire ingestion process: insert into staging, upsert, and delete staging table.

        :param df: The DataFrame containing the data to ingest.
        :param sep: The delimiter used in the COPY command (default is tab).
        :param null_value: How to represent NULL values in the table (default is None).
        """

        if self.checkpoint_manager.is_file_processed(file_name, self.target_table_name):
            print(f"File {file_name} has already been processed. Skipping ingestion.")
            return
        
        self.insert_into_staging(df, sep=sep, null_value=null_value)
        self.upsert_from_staging()
        self.delete_staging_table()
        print(f"Ingestion into {self.target_table_name} completed successfully.")