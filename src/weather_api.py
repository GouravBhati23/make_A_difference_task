import logging
import time

import requests


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snowfall",
    "weather_code",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
    "wind_speed_10m",
    "wind_speed_100m",
    "wind_direction_10m",
    "wind_direction_100m",
    "wind_gusts_10m",
]


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Validate API response
# ---------------------------------------------------------

def validate_response(data):
    """
    Validate the basic structure of the Open-Meteo response.
    """

    if not isinstance(data, dict):
        raise ValueError("API response is not a JSON object")

    if data.get("error") is True:
        reason = data.get("reason", "Unknown API error")
        raise ValueError(f"Open-Meteo API error: {reason}")

    required_fields = [
        "latitude",
        "longitude",
        "timezone",
        "hourly"
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(
                f"Required field missing from API response: {field}"
            )

    hourly = data["hourly"]

    if not isinstance(hourly, dict):
        raise ValueError("'hourly' field is not an object")

    if "time" not in hourly:
        raise ValueError(
            "'time' field missing from hourly response"
        )

    return True


# ---------------------------------------------------------
# API request
# ---------------------------------------------------------

def get_weather_data(
    latitude,
    longitude,
    start_date,
    end_date,
    max_retries=3
):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "Asia/Kolkata"
    }

    for attempt in range(1, max_retries + 1):

        try:

            logger.info(
                "Requesting weather data | "
                "lat=%s | lon=%s | start=%s | end=%s | attempt=%s",
                latitude,
                longitude,
                start_date,
                end_date,
                attempt
            )

            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )

            logger.info(
                "API response status: %s",
                response.status_code
            )

            response.raise_for_status()

            data = response.json()

            validate_response(data)

            logger.info(
                "Successfully received weather data"
            )

            return data

        except requests.exceptions.Timeout:

            logger.warning(
                "API request timed out. Attempt %s/%s",
                attempt,
                max_retries
            )

        except requests.exceptions.ConnectionError:

            logger.warning(
                "Connection error. Attempt %s/%s",
                attempt,
                max_retries
            )

        except requests.exceptions.HTTPError as e:

            logger.warning(
                "HTTP error: %s. Attempt %s/%s",
                e,
                attempt,
                max_retries
            )

        except ValueError as e:

            logger.error(
                "Invalid API response: %s",
                e
            )

            # Don't retry malformed responses.
            raise

        except requests.exceptions.RequestException as e:

            logger.warning(
                "Request failed: %s. Attempt %s/%s",
                e,
                attempt,
                max_retries
            )

        # Exponential backoff
        if attempt < max_retries:

            wait_time = 2 ** (attempt - 1)

            logger.info(
                "Waiting %s seconds before retry",
                wait_time
            )

            time.sleep(wait_time)

    raise RuntimeError(
        f"Weather API failed after {max_retries} attempts"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    data = get_weather_data(
        latitude=26.9124,
        longitude=75.7873,
        start_date="2026-08-01",
        end_date="2026-08-01"
    )

    print()
    print("========== API SUMMARY ==========")

    print("Latitude:", data["latitude"])
    print("Longitude:", data["longitude"])
    print("Timezone:", data["timezone"])
    print("Elevation:", data["elevation"])

    hourly = data["hourly"]

    print(
        "Number of observations:",
        len(hourly["time"])
    )

    print(
        "First timestamp:",
        hourly["time"][0]
    )

    print(
        "First temperature:",
        hourly["temperature_2m"][0]
    )

    print(
        "First humidity:",
        hourly["relative_humidity_2m"][0]
    )