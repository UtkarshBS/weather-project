CREATE TABLE IF NOT EXISTS weather_data (
    station_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    max_temp FLOAT,
    min_temp FLOAT,
    precipitation FLOAT,
    PRIMARY KEY (station_id, date)
);