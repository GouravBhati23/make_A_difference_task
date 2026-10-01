import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

from weather_api import get_weather_data
from database import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent
LOCATIONS_FILE = BASE_DIR / "data" / "location.csv"


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

END_DATE = datetime.now().date()
START_DATE = END_DATE - timedelta(days=29)

START_DATE = START_DATE.isoformat()
END_DATE = END_DATE.isoformat()


# ---------------------------------------------------------
# LOAD LOCATIONS
# ---------------------------------------------------------

def load_locations():

    locations = []

    with open(
        LOCATIONS_FILE,
        mode="r",
        encoding="utf-8"
    ) as file:

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


# ---------------------------------------------------------
# INSERT RAW API RESPONSE
# ---------------------------------------------------------

def insert_raw_response(
    location_id,
    start_date,
    end_date,
    http_status,
    response_json,
    ingestion_status,
    error_message=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO raw_weather_api (
            location_id,
            request_start_date,
            request_end_date,
            fetched_at,
            http_status,
            response_json,
            ingestion_status,
            error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location_id,
            start_date,
            end_date,
            datetime.now().isoformat(),
            http_status,
            json.dumps(response_json),
            ingestion_status,
            error_message
        )
    )

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# INGESTION
# ---------------------------------------------------------

def run_ingestion():

    locations = load_locations()

    print()
    print("==============================================")
    print("          WEATHER DATA INGESTION")
    print("==============================================")
    print(f"Total locations : {len(locations)}")
    print(f"Start date      : {START_DATE}")
    print(f"End date        : {END_DATE}")
    print("Expected hours  : 720 per location")
    print("Expected rows   : approximately 72,000")
    print("==============================================")

    successful = 0
    failed = 0

    for index, location in enumerate(locations, start=1):

        location_id = location["location_id"]
        city = location["city_name"]
        state = location["state_name"]

        latitude = location["latitude"]
        longitude = location["longitude"]

        print()
        print(
            f"[{index}/{len(locations)}] "
            f"Processing: {city}, {state}"
        )

        try:

            data = get_weather_data(
                latitude=latitude,
                longitude=longitude,
                start_date=START_DATE,
                end_date=END_DATE
            )

            insert_raw_response(
                location_id=location_id,
                start_date=START_DATE,
                end_date=END_DATE,
                http_status=200,
                response_json=data,
                ingestion_status="SUCCESS"
            )

            successful += 1

            observation_count = len(
                data["hourly"]["time"]
            )

            print(
                f"SUCCESS: {city} | "
                f"Hourly observations: {observation_count}"
            )

        except Exception as e:

            failed += 1

            print(
                f"FAILED: {city} | "
                f"Error: {e}"
            )

            insert_raw_response(
                location_id=location_id,
                start_date=START_DATE,
                end_date=END_DATE,
                http_status=None,
                response_json={},
                ingestion_status="FAILED",
                error_message=str(e)
            )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print("==============================================")
    print("             INGESTION SUMMARY")
    print("==============================================")
    print(f"Total locations : {len(locations)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {failed}")
    print("==============================================")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    run_ingestion()