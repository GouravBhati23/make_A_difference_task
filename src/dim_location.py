import csv
from database import get_connection
from weather_api import get_weather_data

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOCATIONS_FILE = BASE_DIR / "data" / "location.csv"


def create_location_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_location (
            location_id INTEGER PRIMARY KEY,
            state_code TEXT NOT NULL,
            state_name TEXT NOT NULL,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            api_latitude REAL,
            api_longitude REAL,
            timezone TEXT,
            elevation REAL
        )
    """)

    connection.commit()
    connection.close()

    print("dim_location table created successfully.")


def load_locations():
    locations = []

    with open(LOCATIONS_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            locations.append({
                "location_id": int(row["location_id"]),
                "state_code": row["state_code"],
                "state_name": row["state_name"],
                "city_name": row["city_name"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"])
            })

    return locations


def populate_location_table():

    locations = load_locations()

    connection = get_connection()
    cursor = connection.cursor()

    for location in locations:

        print(
            f"Processing location: "
            f"{location['city_name']} | "
            f"{location['state_name']}"
        )

        try:

            # We only need API metadata here.
            # One day is enough to get timezone/elevation
            # and the API's actual grid coordinates.
            data = get_weather_data(
                latitude=location["latitude"],
                longitude=location["longitude"],
                start_date="2026-08-01",
                end_date="2026-08-01"
            )

            cursor.execute("""
                INSERT OR REPLACE INTO dim_location (
                    location_id,
                    state_code,
                    state_name,
                    city_name,
                    latitude,
                    longitude,
                    api_latitude,
                    api_longitude,
                    timezone,
                    elevation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                location["location_id"],
                location["state_code"],
                location["state_name"],
                location["city_name"],
                location["latitude"],
                location["longitude"],
                data.get("latitude"),
                data.get("longitude"),
                data.get("timezone"),
                data.get("elevation")
            ))

            print(f"SUCCESS: {location['city_name']}")

        except Exception as e:

            print(
                f"FAILED: "
                f"{location['city_name']} | "
                f"{e}"
            )

    connection.commit()
    connection.close()

    print()
    print("Location dimension populated successfully.")


if __name__ == "__main__":

    create_location_table()

    populate_location_table()