from src.services.db_utils import execute_query, fetch_query

class CheckpointManager:
    def __init__(self, checkpoint_table_name='checkpoints'):
        """
        Initialize the CheckpointManager class.
        
        :param checkpoint_table_name: The name of the checkpoint table in the database (default is 'checkpoints').
        """
        self.checkpoint_table_name = checkpoint_table_name
        self._create_checkpoint_table()

    def _create_checkpoint_table(self):
        """
        Create the checkpoint table if it doesn't already exist.
        """
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.checkpoint_table_name} (
            file_name VARCHAR NOT NULL,
            target_table VARCHAR NOT NULL,
            PRIMARY KEY (file_name, target_table)
        );
        """
        execute_query(create_table_query)

    def is_file_processed(self, file_name, target_table):
        """
        Check if a file has already been processed for the specified target table.

        :param file_name: The name of the file to check.
        :param target_table: The name of the target table.
        :return: True if the file has already been processed, False otherwise.
        """
        check_query = f"""
        SELECT 1 FROM {self.checkpoint_table_name}
        WHERE file_name = %s AND target_table = %s;
        """
        result = fetch_query(check_query, (file_name, target_table))
        return len(result) > 0

    def log_file_processed(self, file_name, target_table):
        """
        Log a file as processed in the checkpoint table.

        :param file_name: The name of the file to log.
        :param target_table: The name of the target table.
        """
        insert_query = f"""
        INSERT INTO {self.checkpoint_table_name} (file_name, target_table)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
        """
        execute_query(insert_query, (file_name, target_table))
