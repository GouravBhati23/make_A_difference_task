from database import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("""
    SELECT
        raw_id,
        location_id,
        request_start_date,
        request_end_date,
        ingestion_status
    FROM raw_weather_api
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()