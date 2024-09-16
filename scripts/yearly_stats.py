import pandas as pd
from src.services.db_utils import execute_query, fetch_query

def calculate_yearly_stats():
    query = """
    SELECT station_id, date, max_temp, min_temp, precipitation
    FROM weather_data
    WHERE max_temp IS NOT NULL
      OR min_temp IS NOT NULL
      OR precipitation IS NOT NULL;
    """

    data = fetch_query(query)
    df = pd.DataFrame(data, columns=['station_id', 'date', 'max_temp', 'min_temp', 'precipitation'])
    df['year'] = df['date'].str[:4].astype(int)

    yearly_stats = df.groupby(['station_id', 'year']).agg(
        avg_max_temp=('max_temp', 'mean'),
        avg_min_temp=('min_temp', 'mean'),
        total_precipitation=('precipitation', 'sum')
    ).reset_index()

    # Replaces NaN with None for missing values (for database compatibility)
    yearly_stats = yearly_stats.where(pd.notnull(yearly_stats), None)

    # Inserting the results into the weather_yearly_stats table. I know INSERT INTO by iterating row by row may not be ideal but it's almost 6AM. Best I can do.
    for _, row in yearly_stats.iterrows():
        insert_query = """
        INSERT INTO weather_yearly_stats (station_id, year, avg_max_temp, avg_min_temp, total_precipitation)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (station_id, year)
        DO UPDATE SET 
            avg_max_temp = EXCLUDED.avg_max_temp,
            avg_min_temp = EXCLUDED.avg_min_temp,
            total_precipitation = EXCLUDED.total_precipitation;
        """
        execute_query(insert_query, (row['station_id'], row['year'], row['avg_max_temp'], row['avg_min_temp'], row['total_precipitation']))

    print("Yearly statistics calculated and stored successfully.")

calculate_yearly_stats()