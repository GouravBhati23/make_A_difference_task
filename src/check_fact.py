from database import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT COUNT(*)
    FROM fact_weather_hourly
""")

count = cursor.fetchone()[0]

print("Total hourly rows:", count)


cursor.execute("""
    SELECT
        location_id,
        observation_time,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        wind_speed_10m
    FROM fact_weather_hourly
    ORDER BY location_id, observation_time
    LIMIT 10
""")

rows = cursor.fetchall()

print()
print("Sample records:")

for row in rows:
    print(row)

connection.close()