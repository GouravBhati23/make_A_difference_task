import json
from database import get_connection


def create_fact_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_weather_hourly (
            weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            observation_time TEXT NOT NULL,

            temperature_2m REAL,
            relative_humidity_2m REAL,
            dew_point_2m REAL,
            apparent_temperature REAL,

            precipitation REAL,
            rain REAL,
            snowfall REAL,

            weather_code INTEGER,

            pressure_msl REAL,
            surface_pressure REAL,

            cloud_cover REAL,
            cloud_cover_low REAL,
            cloud_cover_mid REAL,
            cloud_cover_high REAL,

            wind_speed_10m REAL,
            wind_speed_100m REAL,
            wind_direction_10m REAL,
            wind_direction_100m REAL,
            wind_gusts_10m REAL,

            UNIQUE(location_id, observation_time)
        )
    """)

    connection.commit()
    connection.close()

    print("fact_weather_hourly table created successfully.")


def transform_raw_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            raw_id,
            location_id,
            response_json
        FROM raw_weather_api
        WHERE ingestion_status = 'SUCCESS'
    """)

    rows = cursor.fetchall()

    print(f"Raw successful records found: {len(rows)}")

    total_inserted = 0

    for raw_id, location_id, response_json in rows:

        print()
        print(
            f"Processing raw_id={raw_id} | "
            f"location_id={location_id}"
        )

        data = json.loads(response_json)

        hourly = data["hourly"]

        times = hourly["time"]

        print(f"Hourly observations: {len(times)}")

        for i, observation_time in enumerate(times):

            cursor.execute("""
                INSERT OR IGNORE INTO fact_weather_hourly (
                    location_id,
                    observation_time,

                    temperature_2m,
                    relative_humidity_2m,
                    dew_point_2m,
                    apparent_temperature,

                    precipitation,
                    rain,
                    snowfall,

                    weather_code,

                    pressure_msl,
                    surface_pressure,

                    cloud_cover,
                    cloud_cover_low,
                    cloud_cover_mid,
                    cloud_cover_high,

                    wind_speed_10m,
                    wind_speed_100m,
                    wind_direction_10m,
                    wind_direction_100m,
                    wind_gusts_10m
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                location_id,
                observation_time,

                hourly["temperature_2m"][i],
                hourly["relative_humidity_2m"][i],
                hourly["dew_point_2m"][i],
                hourly["apparent_temperature"][i],

                hourly["precipitation"][i],
                hourly["rain"][i],
                hourly["snowfall"][i],

                hourly["weather_code"][i],

                hourly["pressure_msl"][i],
                hourly["surface_pressure"][i],

                hourly["cloud_cover"][i],
                hourly["cloud_cover_low"][i],
                hourly["cloud_cover_mid"][i],
                hourly["cloud_cover_high"][i],

                hourly["wind_speed_10m"][i],
                hourly["wind_speed_100m"][i],
                hourly["wind_direction_10m"][i],
                hourly["wind_direction_100m"][i],
                hourly["wind_gusts_10m"][i]
            ))

            total_inserted += cursor.rowcount

    connection.commit()
    connection.close()

    print()
    print("====================================")
    print(f"Rows inserted: {total_inserted}")
    print("Transformation completed.")
    print("====================================")


if __name__ == "__main__":

    create_fact_table()

    transform_raw_data()