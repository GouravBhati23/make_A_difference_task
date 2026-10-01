from database import get_connection


connection = get_connection()
cursor = connection.cursor()


cursor.execute("""
    SELECT COUNT(*)
    FROM fact_weather_daily
""")

count = cursor.fetchone()[0]

print("Total daily records:", count)


print()
print("Sample daily records:")


cursor.execute("""
    SELECT
        location_id,
        weather_date,
        avg_temperature_2m,
        min_temperature_2m,
        max_temperature_2m,
        avg_relative_humidity_2m,
        total_precipitation,
        max_wind_speed_10m,
        rainy_hours
    FROM fact_weather_daily

    ORDER BY
        location_id,
        weather_date

    LIMIT 10
""")


rows = cursor.fetchall()


for row in rows:
    print(row)


connection.close()