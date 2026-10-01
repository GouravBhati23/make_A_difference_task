import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "weather.db"


def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    return connection


def create_tables():
    """
    Create the raw weather table if it does not already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_weather_api (

            raw_id INTEGER PRIMARY KEY AUTOINCREMENT,

            location_id INTEGER NOT NULL,

            request_start_date TEXT NOT NULL,

            request_end_date TEXT NOT NULL,

            fetched_at TEXT NOT NULL,

            http_status INTEGER,

            response_json TEXT,

            ingestion_status TEXT NOT NULL,

            error_message TEXT

        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":

    create_tables()

    print("Database created successfully.")
    print(f"Database location: {DB_PATH}")