# Weather Data Engineering Pipeline & Dashboard

## 1. Overview

This project is a small end-to-end data engineering pipeline built for
the Data Engineer take-home assignment.

The pipeline uses the **Open-Meteo Historical Weather API** as a free
public data source and turns hourly weather observations for 100
locations in India into:

-   a raw API layer
-   a structured hourly fact table
-   a daily aggregated fact table
-   reporting-ready summary tables
-   an interactive Streamlit dashboard

The project is intentionally lightweight and uses **SQLite + Python +
Streamlit**. Production infrastructure and orchestration are outside the
scope of this assignment.

API: https://archive-api.open-meteo.com/v1/archive

Documentation: https://open-meteo.com/en/docs/historical-weather-api


## 2. Assignment Alignment

The assignment asks for a pipeline that:

-   pulls data from a public API and lands it in a local database
-   models raw API responses into clean structured tables
-   handles real-world API issues
-   produces a meaningful aggregation or trend
-   visualizes the result in a dashboard
-   documents the approach, assumptions, tradeoffs, and AI usage

This project addresses those requirements with a raw → modeled →
reporting architecture.


## 3. Dataset

The pipeline currently uses:

-   **100 locations**
-   **30 calendar days**
-   **24 hourly observations per location per day**
-   Approximately **72,000 hourly observations**
-   Approximately **3,000 daily records**
-   Locations distributed across **34 states/UT-level regions
    represented in the location dataset**

The location metadata is maintained in:

``` text
data/locations.csv
```

The database is generated locally at:

``` text
data/weather.db
```

The SQLite database is a generated artifact and does not need to be
committed to GitHub.

## 4. Architecture

``` text
                    Open-Meteo API
                          |
                          v
                +--------------------+
                |   Raw API Layer    |
                | raw_weather_api    |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Hourly Transformation|
                | fact_weather_hourly |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Daily Aggregation  |
                | fact_weather_daily |
                +---------+----------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
       +-------------+       +----------------------+
       | dim_location|       | Reporting Layer      |
       |             |       | state_weather        |
       +-------------+       | daily_weather        |
                             +----------+-----------+
                                        |
                                        v
                              +-------------------+
                              | Streamlit Dashboard|
                              +-------------------+
```

## 5. Data Model

### `raw_weather_api`

The raw table stores one complete API response per location/request.

Important fields:

-   `raw_id`
-   `location_id`
-   `request_start_date`
-   `request_end_date`
-   `fetched_at`
-   `http_status`
-   `response_json`
-   `ingestion_status`
-   `error_message`

Keeping the original JSON response makes the raw layer traceable and
allows transformations to be rerun without calling the API again.

### `dim_location`

Location dimension containing:

-   `location_id`
-   `state_code`
-   `state_name`
-   `city_name`
-   requested latitude/longitude
-   API-returned latitude/longitude
-   timezone
-   elevation

The requested coordinates and API-returned coordinates are both retained
because the API may map a requested location to a nearby weather-model
grid point.

### `fact_weather_hourly`

Grain:

> One row = one location + one hourly observation.

The table contains temperature, humidity, precipitation, pressure, cloud
cover, wind and weather-code measurements.

Current volume:

``` text
~72,000 rows
```

### `fact_weather_daily`

Grain:

> One row = one location + one calendar day.

Daily metrics include:

-   average/minimum/maximum temperature
-   average humidity
-   total precipitation
-   total rain
-   total snowfall
-   average/max wind speed
-   average pressure
-   average cloud cover
-   rainy hours

Current volume:

``` text
~3,000 rows
```

### Reporting tables

The reporting layer contains dashboard-oriented aggregations:

-   state-level weather summary
-   overall daily weather trend

This keeps dashboard queries simpler and separates reporting logic from
the detailed fact tables.

## 6. Pipeline Flow

### Step 1 --- Load location metadata

`data/locations.csv` provides the list of locations and coordinates.

### Step 2 --- Extract

`src/weather_api.py` calls Open-Meteo for each location and date range.

The API client includes:

-   request timeout
-   response validation
-   HTTP error handling
-   connection error handling
-   retry logic
-   exponential backoff
-   validation of required response fields

### Step 3 --- Raw ingestion

`src/ingest.py` requests 30 days of hourly data for each location and
stores the complete JSON response in `raw_weather_api`.

The current run processes:

``` text
100 locations
x 30 days
x 24 hours
= 72,000 hourly observations
```

### Step 4 --- Hourly transformation

`src/tranform.py` converts the API's parallel hourly arrays into one
row per location/timestamp.

For example:

``` text
time[0] + temperature[0] + humidity[0] + precipitation[0]
```

becomes one relational row.

### Step 5 --- Daily aggregation

`src/daily_aggregation_db.py` aggregates hourly observations into daily
metrics.

### Step 6 --- Reporting

`src/reporting_db.py` creates state-level and daily trend datasets for
dashboard consumption.

### Step 7 --- Visualization

`dashboard.py` provides the Streamlit dashboard.


### Pagination

The selected Open-Meteo historical endpoint returns the requested hourly
range directly, so pagination is **not required for this endpoint**.
Instead of inventing pagination logic, the pipeline processes one API
response per location.

### Rate limits

The pipeline keeps the ingestion workload intentionally small: one
request per location for the selected date range. HTTP failures are
retried with backoff.

For a production implementation, I would add explicit handling for HTTP
429 and server-side 5xx responses with configurable retry limits and
possibly request throttling.

## 7. Meaningful Metrics

The project focuses on metrics that are understandable to both technical
and non-technical users:

### Temperature

-   average temperature
-   minimum temperature
-   maximum temperature
-   daily temperature trend

### Precipitation

-   total precipitation
-   total rain
-   rainy hours

### Humidity

-   average relative humidity

### Wind

-   average wind speed
-   maximum wind speed

The dashboard combines these metrics to provide both time-series and
location/state comparisons.

## 8. Dashboard

The Streamlit dashboard provides:

-   average temperature KPI
-   average humidity KPI
-   total precipitation KPI
-   maximum wind-speed KPI
-   30-day temperature trend
-   state-level average-temperature comparison
-   state-level precipitation comparison
-   location-level summary table
-   state filter
-   location filter

Run the dashboard with:

``` bash
streamlit run dashboard.py
```

The dashboard is designed to be understandable without requiring
knowledge of the underlying API.

## 9. Project Structure

``` text
make_A_difference_task/
|
├── data/
│   └── location.csv
|
├── src/
│   ├── __init__.py
│   ├── weather_api.py
│   ├── database.py
│   ├── ingest.py
│   ├── tranform.py
│   ├── dim_location.py
│   ├── daily_aggregation_db.py
│   └── reporting_db.py
|
|
├── dashboard.py
├── requirements.txt
├── README.md
```

## 10. Setup

### Prerequisites

-   Python 3.10+
-   pip
-   Internet access for the Open-Meteo API

No API key is required for this project.

### Create virtual environment

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

``` bash
pip install -r requirements.txt
```

## 11. Run the Pipeline

Run the commands from the `src` directory where applicable.

### 1. Create database tables

``` bash
python database.py
```

### 2. Ingest API data

``` bash
python ingest.py
```

### 3. Create/populate location dimension

``` bash
python dim_location.py
```

### 4. Transform raw responses into hourly facts

``` bash
python tranform.py
```

### 5. Aggregate hourly data into daily data

``` bash
python daily_aggregation_db.py
```

### 6. Create reporting tables

``` bash
python reporting_db.py
```

### 7. Start dashboard

From the project root:

``` bash
streamlit run dashboard.py
```

## 12. Assumptions

1.  The project uses 100 representative locations rather than every city
    in India.
2.  The analysis window is 30 calendar days.
3.  The weather observation timezone is requested as `Asia/Kolkata`.
4.  The API's returned model/grid coordinates are retained separately
    from the requested coordinates.
5.  Hourly records are treated as the detailed analytical grain.
6.  Daily aggregation is based on the hourly records stored in SQLite.
7.  The local SQLite database is sufficient for the assignment scope.

## 13. Tradeoffs

### SQLite instead of PostgreSQL
SQLite was selected because:
-   it requires no database server
-   it is easy to reproduce locally

### Python transformations instead of dbt
Plain Python/SQL transformations were used to keep the implementation
compact and easy to run.

### 30 days instead of a longer history
A 30-day window provides enough data for meaningful trends while keeping
API ingestion and local processing lightweight.


## 14. Results

The final local pipeline currently produces approximately:

  Layer                       Records
  ------------------------- ---------
  Locations                       100
  Raw API responses               100
  Hourly weather facts         72,000
  Daily weather facts           3,000
  State reporting records          34
  Daily reporting records          30

The dashboard consumes the modeled/reporting data rather than the raw
API JSON.


## 15. Conclusion

This project demonstrates an end-to-end data engineering workflow:

``` text
Public API
    ↓
Raw ingestion
    ↓
Structured hourly data
    ↓
Daily aggregation
    ↓
Reporting layer
    ↓
Interactive dashboard
```

The design prioritizes clear data modeling, traceability, practical API
error handling, meaningful aggregation, and reproducibility within the
time-box of the assignment.
