import os
import pandas as pd
from src.services.ingest import Ingestor

# Defines the table "schema"
columns = {
    'station_id': 'VARCHAR',
    'date': 'DATE',
    'max_temp': 'FLOAT',
    'min_temp': 'FLOAT',
    'precipitation': 'FLOAT'
}

# Creates an instance of the Ingestor class
ingestor = Ingestor(
    target_table_name='weather_data',
    staging_table_name='weather_data_staging',
    column_definitions=columns,
    conflict_columns=['station_id', 'date'],
    update_columns=['max_temp', 'min_temp', 'precipitation']
)

data_dir = '../data/wx_data'

for file_name in os.listdir(data_dir):
    file_path = os.path.join(data_dir, file_name)

    # Only process .txt files because we don't want to process random datasets if they arrive or auto generated files either
    if file_name.endswith('.txt'):
        print(f"Processing file: {file_name}")
        df = pd.read_csv(file_path, sep='\t', header=None, names=["date", "max_temp", "min_temp", "precipitation"])
        station_id = os.path.splitext(file_name)[0]

        # Below code is basic QC
        df['station_id'] = station_id
        df['date'] = df['date'].astype(str)
        df['max_temp'] = df['max_temp'].replace(-9999, None) / 10.0
        df['min_temp'] = df['min_temp'].replace(-9999, None) / 10.0
        df['precipitation'] = df['precipitation'].replace(-9999, None) / 10.0

        # Reorder the DataFrame to match the table structure (station_id, date, max_temp, min_temp, precipitation)
        df = df[['station_id', 'date', 'max_temp', 'min_temp', 'precipitation']]

        # Call the Ingestor to handle the ingestion
        ingestor.ingest_table(file_name, df)

        print(f"Finished processing {file_name}\n")
