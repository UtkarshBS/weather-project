
# Weather Data Pipeline and API

This repository contains a weather data ingestion pipeline and a REST API built using **Flask** and **PostgreSQL**. It ingests raw weather data from text files, stores it in a PostgreSQL database, and exposes a set of endpoints to retrieve and analyze the data.

## Features

- **Data Ingestion**: Reads weather data from text files and stores it in PostgreSQL.
- **Checkpointing**: Ensures each data file is ingested only once.
- **REST API**: Allows querying weather data and calculating yearly statistics for stations.
- **Kubernetes**: Ready to deploy on EKS with Kubernetes manifests.
- **Automated CI/CD**: Includes a Jenkins pipeline for automating the deployment and ingestion.

---

## How to Run

### Step 1: Clone the repository

```markdown
# Clone the repository:
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

### Step 2: Install dependencies

```markdown
# Install dependencies:
pip install -r requirements.txt
```

---

### Step 3: Set up your PostgreSQL database

```markdown
# Set up PostgreSQL database:
Make sure PostgreSQL is running and the following tables are created:
- `weather_data`
- `weather_yearly_stats`

You can find SQL scripts to create these tables in the `migrations/` directory.
```

### Step 4: Run the Flask API

```markdown
# Run the Flask API:
python scripts/api.py
```

This will start the Flask API on `http://localhost:5000`.

---

### Step 5: Run the ingestion process

```markdown
# Ingest all files from wx_data folder:
python scripts/weather_ingestion.py
```

This will ingest all the weather data files from the specified directory.

---

## Configuration

```markdown
# Configuration:
- **PostgreSQL Connection**: Modify the PostgreSQL connection string in `src/config/connectors.py` or use the `DATABASE_URL` environment variable.
- **API Port**: The API runs on port `5000` by default. You can change this in `api.py` if needed.
```

---

## API Endpoints

The API exposes two endpoints for querying weather data and statistics.

### 1. **/api/weather** (GET)

Fetches weather data filtered by `station_id` and `date`. Supports pagination with `limit` and `offset`.

#### Query Parameters:
- `station_id`: The ID of the weather station (optional).
- `date`: The date for which you want the weather data (optional).
- `limit`: The number of records to return (default: 10).
- `offset`: The starting point for pagination (default: 0).

#### Example Request:
```markdown
GET /api/weather?station_id=station1&date=2024-09-15&limit=5
```

#### Example Response:
```json
[
  {
    "station_id": "station1",
    "date": "2024-09-15",
    "max_temp": 25.5,
    "min_temp": 15.0,
    "precipitation": 12.3
  }
]
```

---

### 2. **/api/weather/stats** (GET)

Fetches weather statistics (average max/min temperatures and total precipitation) for a weather station and year. Supports pagination.

#### Query Parameters:
- `station_id`: The ID of the weather station (optional).
- `year`: The year for which you want statistics (optional).
- `limit`: The number of records to return (default: 10).
- `offset`: The starting point for pagination (default: 0).

#### Example Request:
```markdown
GET /api/weather/stats?station_id=station1&year=2024&limit=5
```

#### Example Response:
```json
[
  {
    "station_id": "station1",
    "year": 2024,
    "avg_max_temp": 25.3,
    "avg_min_temp": 15.1,
    "total_precipitation": 230.5
  }
]
```

---

## Ingestion Process

The ingestion pipeline reads raw weather data files from the `wx_data/` folder, processes them, and inserts them into the PostgreSQL database. The system uses checkpointing to ensure that each file is only processed once.

```markdown
# Run the ingestion manually:
python scripts/weather_ingestion.py
```

- **Ingestion Logic**: The ingestion logic is implemented in the `Ingestor` class located in `src/services/ingestor.py`.
- **Checkpointing**: Files that are processed are logged in the `checkpoints` table, ensuring they are not processed again.

---

## Deployment

The repository includes configurations for deploying the Flask API and ingestion pipeline to **AWS** using **EKS** and **Jenkins**.

### 1. **Docker Setup**

```markdown
# Dockerfile to containerize Flask API:
```

A `Dockerfile` is provided to containerize the Flask API and ingestion jobs.

---

## Swagger/OpenAPI Documentation

The API includes **Swagger** documentation to provide a visual interface for testing the API.

```markdown
# Swagger URL:
Visit `http://localhost:5000/swagger` to access the Swagger UI. The OpenAPI spec is located at `static/swagger.json`.
```
