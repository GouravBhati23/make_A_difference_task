from database import get_connection


def create_reporting_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # STATE WEATHER SUMMARY
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reporting_state_weather (
            state_name TEXT PRIMARY KEY,

            avg_temperature REAL,
            min_temperature REAL,
            max_temperature REAL,

            avg_humidity REAL,

            total_precipitation REAL,
            total_rain REAL,

            avg_wind_speed REAL,
            max_wind_speed REAL,

            total_rainy_hours INTEGER,

            location_count INTEGER
        )
    """)

    # ---------------------------------------------------------
    # DAILY WEATHER TREND
    # ---------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reporting_daily_weather (
            weather_date TEXT PRIMARY KEY,

            avg_temperature REAL,
            min_temperature REAL,
            max_temperature REAL,

            avg_humidity REAL,

            total_precipitation REAL,
            total_rain,

            avg_wind_speed REAL,
            max_wind_speed REAL,

            rainy_hours INTEGER
        )
    """)

    connection.commit()
    connection.close()

    print("Reporting tables created successfully.")


def populate_state_summary():

    connection = get_connection()
    cursor = connection.cursor()

    # Clear previous reporting data
    cursor.execute("""
        DELETE FROM reporting_state_weather
    """)

    cursor.execute("""
        INSERT INTO reporting_state_weather (
            state_name,
            avg_temperature,
            min_temperature,
            max_temperature,
            avg_humidity,
            total_precipitation,
            total_rain,
            avg_wind_speed,
            max_wind_speed,
            total_rainy_hours,
            location_count
        )

        SELECT
            dl.state_name,

            ROUND(AVG(fd.avg_temperature_2m), 2),
            ROUND(MIN(fd.min_temperature_2m), 2),
            ROUND(MAX(fd.max_temperature_2m), 2),

            ROUND(AVG(fd.avg_relative_humidity_2m), 2),

            ROUND(SUM(fd.total_precipitation), 2),
            ROUND(SUM(fd.total_rain), 2),

            ROUND(AVG(fd.avg_wind_speed_10m), 2),
            ROUND(MAX(fd.max_wind_speed_10m), 2),

            SUM(fd.rainy_hours),

            COUNT(DISTINCT dl.location_id)

        FROM fact_weather_daily fd

        INNER JOIN dim_location dl
            ON fd.location_id = dl.location_id

        GROUP BY
            dl.state_name
    """)

    connection.commit()
    connection.close()

    print("State weather summary populated.")


def populate_daily_trend():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM reporting_daily_weather
    """)

    cursor.execute("""
        INSERT INTO reporting_daily_weather (
            weather_date,
            avg_temperature,
            min_temperature,
            max_temperature,
            avg_humidity,
            total_precipitation,
            total_rain,
            avg_wind_speed,
            max_wind_speed,
            rainy_hours
        )

        SELECT
            weather_date,

            ROUND(AVG(avg_temperature_2m), 2),
            ROUND(MIN(min_temperature_2m), 2),
            ROUND(MAX(max_temperature_2m), 2),

            ROUND(AVG(avg_relative_humidity_2m), 2),

            ROUND(SUM(total_precipitation), 2),
            ROUND(SUM(total_rain), 2),

            ROUND(AVG(avg_wind_speed_10m), 2),
            ROUND(MAX(max_wind_speed_10m), 2),

            SUM(rainy_hours)

        FROM fact_weather_daily

        GROUP BY
            weather_date

        ORDER BY
            weather_date
    """)

    connection.commit()
    connection.close()

    print("Daily weather trend populated.")


def run_reporting():

    print()
    print("====================================")
    print("Creating reporting layer")
    print("====================================")

    create_reporting_tables()

    populate_state_summary()

    populate_daily_trend()

    print()
    print("Reporting layer completed.")


if __name__ == "__main__":
    run_reporting()