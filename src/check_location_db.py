from database import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
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
    FROM dim_location
    ORDER BY location_id
""")

rows = cursor.fetchall()

print(f"Total locations: {len(rows)}")
print()

for row in rows:
    print(row)

connection.close()