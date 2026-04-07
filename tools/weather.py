from os import getenv
from dotenv import load_dotenv
import requests
from pathlib import Path
import config

load_dotenv()
load_dotenv(Path(config.DATA_DIR) / ".env")
base_url = "http://api.weatherapi.com/v1"

current_weather_params = ["temp_c", "wind_kph", "precip_mm", "humidity", "cloud", "feelslike_c", "uv"]
forecast_params = ["maxtemp_c", "mintemp_c", "avgtemp_c", "maxwind_kph", "totalprecip_mm", "avghumidity", "uv", "sunrise", "sunset", "moonrise", "moonset", "moon_phase", "moon_illumination"]


def _weather_api_key() -> str | None:
    key = getenv("WEATHER_API_KEY")
    if key:
        return key

    # Re-load in case user wrote key to ~/.jarvis/.env after process start.
    load_dotenv(Path(config.DATA_DIR) / ".env")
    return getenv("WEATHER_API_KEY")


def _request_weather(endpoint: str, params: dict) -> tuple[dict | None, str | None]:
    api_key = _weather_api_key()
    if not api_key:
        return None, "WEATHER_API_KEY is missing. Set it and retry."

    query_params = dict(params)
    query_params["key"] = api_key

    try:
        response = requests.get(f"{base_url}/{endpoint}", params=query_params, timeout=10)
    except requests.exceptions.RequestException as exc:
        return None, f"Weather API request failed: {exc}"

    if response.status_code == 200:
        try:
            return response.json(), None
        except ValueError:
            return None, "Weather API returned invalid JSON."

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    detail = payload.get("error", {}).get("message")
    if not detail:
        detail = f"Weather API returned status {response.status_code}."

    return None, detail


def get_current_weather(city_name: str):
    """If you need to know current weather in any location you can use this tool to get weather by city name.
  
    Args:
      city_name: City you're interested in getting weather in.

    Returns:
      {
      "temp_c": current temperature in degrees Celsius,
      "condition": current weather condition,
      "wind_kph": wind speed in km/h,
      "precip_mm": current preciptation in milimeters,
      "humidity": current humidity,
      "cloud": current cloudiness,
      "feelslike_c": how temperature feels like outside in degrees Celsius,
      "uv": current Ultraviolet radiation
      }
    """
    payload, error = _request_weather("current.json", {"q": city_name})
    if error:
        return error

    data = payload.get("current", {})
    final_responce = {}

    for key, value in data.items():
        if key in current_weather_params:
            final_responce[key] = value
        elif key == "condition":
            final_responce[key] = value["text"]
        
    return final_responce

def get_forecast(city_name: str, days: int):
    """If you need to know weather forecast for max 3 days forward, you can use this tool to get weather forecast by city name.
  
    Args:
      city_name: City you're interested in getting weather in.
      days: how much days from today you want to see forecast(from 0 to 3, 0 - today, 3 - 3 days from today)

    Returns:
      {
      "maxtemp_c": maximum temperature in degrees Celsius,
      "mintemp_c": minimum temperature in degrees Celsius,
      "avgtemp_c": average temperature in degrees Celsius,
      "maxwind_kph": maximum vind speed in km/h,
      "totalprecip_mm": total preciptations in milimeters,
      "cloud": current cloudiness,
      "avghumidity": average humidity,
      "uv": Ultraviolet radiation,
      "sunrise": Time when sun rises,
      "sunset": Time when sun sets,
      "moonrise": Time when moon rises,
      "moonset": Time when moon sets,
      "moon_phase": Current phase of the moon,
      "moon illumination": Visibility of the moon
      }
    """    
    try:
        days = int(days)
    except Exception:
        return "Parameter 'days' must be a number from 0 to 3."

    if days < 0 or days > 3:
        return "Parameter 'days' must be from 0 to 3."

    # WeatherAPI expects number of forecast days including today.
    api_days = days + 1
    payload, error = _request_weather("forecast.json", {"q": city_name, "days": api_days})
    if error:
        return error

    forecast_days = payload.get("forecast", {}).get("forecastday", [])
    if len(forecast_days) <= days:
        return "Forecast data is unavailable for the requested day."

    data = forecast_days[days]
    final_responce = {}

    final_responce["date"] = data["date"]
    for key, value in data["day"].items():
        if key in forecast_params:
            final_responce[key] = value
        elif key == "condition":
            final_responce[key] = value["text"] 
    
    for key, value in data["astro"].items():
        if key in forecast_params:
            final_responce[key] = value

    return final_responce


