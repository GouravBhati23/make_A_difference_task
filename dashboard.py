import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "weather.db"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌦️",
    layout="wide"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def get_connection():

    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )


connection = get_connection()


# =========================================================
# LOAD FILTER VALUES
# =========================================================

@st.cache_data
def load_states():

    query = """
        SELECT DISTINCT state_name
        FROM dim_location
        ORDER BY state_name
    """

    return pd.read_sql_query(query, connection)


@st.cache_data
def load_locations():

    query = """
        SELECT
            location_id,
            city_name,
            state_name
        FROM dim_location
        ORDER BY city_name
    """

    return pd.read_sql_query(query, connection)


states_df = load_states()
locations_df = load_locations()


# =========================================================
# HEADER
# =========================================================

st.title("🌦️ Weather Analytics Dashboard")

st.markdown(
    """
    **30-Day Weather Analysis across 100 locations in India**

    Data source: Open-Meteo Historical Weather API
    """
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")


state_options = ["All States"] + states_df["state_name"].tolist()

selected_state = st.sidebar.selectbox(
    "State",
    state_options
)


if selected_state == "All States":

    location_options = ["All Locations"] + (
        locations_df["city_name"].tolist()
    )

else:

    location_options = ["All Locations"] + (
        locations_df[
            locations_df["state_name"] == selected_state
        ]["city_name"].tolist()
    )


selected_location = st.sidebar.selectbox(
    "Location",
    location_options
)


# =========================================================
# BUILD FILTER CONDITIONS
# =========================================================

conditions = []
parameters = []


if selected_state != "All States":

    conditions.append("dl.state_name = ?")
    parameters.append(selected_state)


if selected_location != "All Locations":

    conditions.append("dl.city_name = ?")
    parameters.append(selected_location)


where_clause = ""

if conditions:

    where_clause = "WHERE " + " AND ".join(conditions)


# =========================================================
# KPI QUERY
# =========================================================

kpi_query = f"""
    SELECT

        ROUND(AVG(fd.avg_temperature_2m), 2)
            AS avg_temperature,

        ROUND(AVG(fd.avg_relative_humidity_2m), 2)
            AS avg_humidity,

        ROUND(SUM(fd.total_precipitation), 2)
            AS total_precipitation,

        ROUND(MAX(fd.max_wind_speed_10m), 2)
            AS max_wind_speed

    FROM fact_weather_daily fd

    INNER JOIN dim_location dl
        ON fd.location_id = dl.location_id

    {where_clause}
"""


kpi_df = pd.read_sql_query(
    kpi_query,
    connection,
    params=parameters
)


# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


avg_temperature = kpi_df.iloc[0]["avg_temperature"]
avg_humidity = kpi_df.iloc[0]["avg_humidity"]
total_precipitation = kpi_df.iloc[0]["total_precipitation"]
max_wind_speed = kpi_df.iloc[0]["max_wind_speed"]


col1.metric(
    "Average Temperature",
    f"{avg_temperature:.2f} °C"
)


col2.metric(
    "Average Humidity",
    f"{avg_humidity:.2f} %"
)


col3.metric(
    "Total Precipitation",
    f"{total_precipitation:.2f} mm"
)


col4.metric(
    "Maximum Wind Speed",
    f"{max_wind_speed:.2f} km/h"
)


st.divider()


# =========================================================
# DAILY TEMPERATURE TREND
# =========================================================

st.subheader("📈 Temperature Trend")


temperature_query = f"""
    SELECT

        fd.weather_date,

        ROUND(AVG(fd.avg_temperature_2m), 2)
            AS avg_temperature,

        ROUND(MIN(fd.min_temperature_2m), 2)
            AS min_temperature,

        ROUND(MAX(fd.max_temperature_2m), 2)
            AS max_temperature

    FROM fact_weather_daily fd

    INNER JOIN dim_location dl
        ON fd.location_id = dl.location_id

    {where_clause}

    GROUP BY fd.weather_date

    ORDER BY fd.weather_date
"""


temperature_df = pd.read_sql_query(
    temperature_query,
    connection,
    params=parameters
)


if not temperature_df.empty:

    temperature_df["weather_date"] = pd.to_datetime(
        temperature_df["weather_date"]
    )

    temperature_df = temperature_df.set_index(
        "weather_date"
    )

    st.line_chart(
        temperature_df[
            [
                "avg_temperature",
                "min_temperature",
                "max_temperature"
            ]
        ]
    )


# =========================================================
# STATE LEVEL ANALYSIS
# =========================================================

st.subheader("🌍 State-level Weather Analysis")


state_query = """
    SELECT

        dl.state_name,

        ROUND(AVG(fd.avg_temperature_2m), 2)
            AS avg_temperature,

        ROUND(SUM(fd.total_precipitation), 2)
            AS total_precipitation,

        ROUND(AVG(fd.avg_relative_humidity_2m), 2)
            AS avg_humidity,

        ROUND(AVG(fd.avg_wind_speed_10m), 2)
            AS avg_wind_speed

    FROM fact_weather_daily fd

    INNER JOIN dim_location dl
        ON fd.location_id = dl.location_id

    GROUP BY dl.state_name

    ORDER BY avg_temperature DESC
"""


state_df = pd.read_sql_query(
    state_query,
    connection
)


col1, col2 = st.columns(2)


with col1:

    st.write("### Average Temperature by State")

    temperature_chart = state_df.set_index(
        "state_name"
    )[["avg_temperature"]]

    st.bar_chart(
        temperature_chart
    )


with col2:

    st.write("### Total Precipitation by State")

    rainfall_chart = state_df.set_index(
        "state_name"
    )[["total_precipitation"]]

    st.bar_chart(
        rainfall_chart
    )


# =========================================================
# LOCATION TABLE
# =========================================================

st.subheader("📍 Location Summary")


location_query = f"""
    SELECT

        dl.state_name,
        dl.city_name,

        ROUND(AVG(fd.avg_temperature_2m), 2)
            AS avg_temperature,

        ROUND(MIN(fd.min_temperature_2m), 2)
            AS min_temperature,

        ROUND(MAX(fd.max_temperature_2m), 2)
            AS max_temperature,

        ROUND(AVG(fd.avg_relative_humidity_2m), 2)
            AS avg_humidity,

        ROUND(SUM(fd.total_precipitation), 2)
            AS total_precipitation,

        SUM(fd.rainy_hours)
            AS rainy_hours

    FROM fact_weather_daily fd

    INNER JOIN dim_location dl
        ON fd.location_id = dl.location_id

    {where_clause}

    GROUP BY
        dl.state_name,
        dl.city_name

    ORDER BY
        dl.state_name,
        dl.city_name
"""


location_df = pd.read_sql_query(
    location_query,
    connection,
    params=parameters
)


st.dataframe(
    location_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Weather data sourced from Open-Meteo Historical Weather API."
)