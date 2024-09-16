CREATE TABLE IF NOT EXISTS weather_yearly_stats (
    station_id VARCHAR NOT NULL,
    year INT NOT NULL,
    avg_max_temp FLOAT,
    avg_min_temp FLOAT,
    total_precipitation FLOAT,
    PRIMARY KEY (station_id, year)
);