from database import get_connection


def create_daily_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_weather_daily (

            daily_weather_id INTEGER PRIMARY KEY AUTOINCREMENT,

            location_id INTEGER NOT NULL,
            weather_date TEXT NOT NULL,

            avg_temperature_2m REAL,
            min_temperature_2m REAL,
            max_temperature_2m REAL,

            avg_relative_humidity_2m REAL,

            total_precipitation REAL,
            total_rain REAL,
            total_snowfall REAL,

            max_wind_speed_10m REAL,
            avg_wind_speed_10m REAL,

            avg_pressure_msl REAL,

            avg_cloud_cover REAL,

            rainy_hours INTEGER,

            UNIQUE(location_id, weather_date)
        )
    """)

    connection.commit()
    connection.close()

    print("fact_weather_daily table created successfully.")


def populate_daily_table():

    connection = get_connection()
    cursor = connection.cursor()

    print()
    print("Starting daily aggregation...")

    cursor.execute("""
        INSERT OR REPLACE INTO fact_weather_daily (
            location_id,
            weather_date,

            avg_temperature_2m,
            min_temperature_2m,
            max_temperature_2m,

            avg_relative_humidity_2m,

            total_precipitation,
            total_rain,
            total_snowfall,

            max_wind_speed_10m,
            avg_wind_speed_10m,

            avg_pressure_msl,

            avg_cloud_cover,

            rainy_hours
        )

        SELECT

            location_id,

            DATE(observation_time) AS weather_date,

            ROUND(AVG(temperature_2m), 2),
            ROUND(MIN(temperature_2m), 2),
            ROUND(MAX(temperature_2m), 2),

            ROUND(AVG(relative_humidity_2m), 2),

            ROUND(SUM(precipitation), 2),
            ROUND(SUM(rain), 2),
            ROUND(SUM(snowfall), 2),

            ROUND(MAX(wind_speed_10m), 2),
            ROUND(AVG(wind_speed_10m), 2),

            ROUND(AVG(pressure_msl), 2),

            ROUND(AVG(cloud_cover), 2),

            SUM(
                CASE
                    WHEN precipitation > 0
                    THEN 1
                    ELSE 0
                END
            )

        FROM fact_weather_hourly

        GROUP BY
            location_id,
            DATE(observation_time)
    """)

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_weather_daily
    """)

    count = cursor.fetchone()[0]

    connection.close()

    print()
    print("====================================")
    print("Daily aggregation completed.")
    print(f"Daily records created: {count}")
    print("====================================")


if __name__ == "__main__":

    create_daily_table()

    populate_daily_table()