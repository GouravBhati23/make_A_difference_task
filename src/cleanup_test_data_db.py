from database import get_connection


def cleanup_old_test_data():

    connection = get_connection()
    cursor = connection.cursor()

    print("Cleaning old test data...")

    # Remove old daily records
    cursor.execute("""
        DELETE FROM fact_weather_daily
        WHERE weather_date < '2026-09-02'
    """)

    daily_deleted = cursor.rowcount

    # Remove old hourly records
    cursor.execute("""
        DELETE FROM fact_weather_hourly
        WHERE DATE(observation_time) < '2026-09-02'
    """)

    hourly_deleted = cursor.rowcount

    # Remove old raw API responses
    cursor.execute("""
        DELETE FROM raw_weather_api
        WHERE request_start_date < '2026-09-02'
    """)

    raw_deleted = cursor.rowcount

    connection.commit()
    connection.close()

    print()
    print("====================================")
    print("Cleanup completed")
    print("====================================")
    print(f"Daily rows deleted  : {daily_deleted}")
    print(f"Hourly rows deleted : {hourly_deleted}")
    print(f"Raw rows deleted    : {raw_deleted}")
    print("====================================")


if __name__ == "__main__":
    cleanup_old_test_data()