from database import get_connection


connection = get_connection()
cursor = connection.cursor()


print("STATE WEATHER SUMMARY")
print("=" * 70)


cursor.execute("""
    SELECT
        state_name,
        avg_temperature,
        min_temperature,
        max_temperature,
        avg_humidity,
        total_precipitation,
        avg_wind_speed,
        total_rainy_hours,
        location_count
    FROM reporting_state_weather
    ORDER BY state_name
""")


rows = cursor.fetchall()


print("Total states:", len(rows))
print()


for row in rows:
    print(row)


print()
print("DAILY WEATHER TREND")
print("=" * 70)


cursor.execute("""
    SELECT
        weather_date,
        avg_temperature,
        min_temperature,
        max_temperature,
        avg_humidity,
        total_precipitation
    FROM reporting_daily_weather
    ORDER BY weather_date
    LIMIT 10
""")


rows = cursor.fetchall()


for row in rows:
    print(row)


connection.close()