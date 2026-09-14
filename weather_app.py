"""A simple live weather CLI powered by Open-Meteo (no API key required)."""

from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Rain showers", 82: "Violent rain showers", 95: "Thunderstorm",
}


def fetch_json(base_url: str, params: dict[str, str]) -> dict:
    """Fetch JSON from a public API with a helpful HTTP user agent."""
    request = Request(f"{base_url}?{urlencode(params)}", headers={"User-Agent": "live-weather-python/1.0"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def get_weather(location: str) -> tuple[dict, dict]:
    places = fetch_json("https://geocoding-api.open-meteo.com/v1/search", {"name": location, "count": "1", "language": "en", "format": "json"})
    if not places.get("results"):
        raise ValueError(f"No location found for {location!r}.")
    place = places["results"][0]
    weather = fetch_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": str(place["latitude"]), "longitude": str(place["longitude"]),
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "timezone": "auto",
    })
    return place, weather["current"]


def main() -> None:
    location = input("Enter a city or place: ").strip()
    if not location:
        print("Please enter a location.")
        return
    try:
        place, current = get_weather(location)
    except Exception as error:
        print(f"Could not fetch weather: {error}")
        return

    label = ", ".join(filter(None, [place.get("name"), place.get("admin1"), place.get("country")]))
    print(f"\nLive weather for {label} ({current['time']})")
    print(f"Condition: {WEATHER_CODES.get(current['weather_code'], 'Unknown')}")
    print(f"Temperature: {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)")
    print(f"Humidity: {current['relative_humidity_2m']}%")
    print(f"Wind: {current['wind_speed_10m']} km/h")


if __name__ == "__main__":
    main()
