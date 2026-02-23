from os import getenv
from dotenv import load_dotenv
import requests
import json

load_dotenv()
api_key=getenv("WEATHER_API_KEY")
base_url="http://api.weatherapi.com/v1"

current_weather_params = ["temp_c", "wind_kph", "precip_mm", "humidity", "cloud", "feelslike_c", "uv"]
forecast_params = ["maxtemp_c", "mintemp_c", "avgtemp_c", "maxwind_kph", "totalprecip_mm", "avghumidity", "uv", "sunrise", "sunset", "moonrise", "moonset", "moon_phase", "moon_illumination"]

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
    params = {
        "key": api_key,
        "q": city_name
    }
    responce = requests.get(base_url + "/current.json", params=params)
    if responce.status_code == 400:
        return "No matching location found. Try another city_name"
    data = responce.json()["current"]
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
    days = int(days)

    params = {
        "key": api_key,
        "q": city_name,
        "days": days
    }
    if days > 3:
        return "Can't get forecast for more than 3 days."
    responce = requests.get(base_url + "/forecast.json", params=params)
    if responce.status_code == 400:
        return "No matching location found. Try another city_name"
    data = responce.json()["forecast"]["forecastday"][0]
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


