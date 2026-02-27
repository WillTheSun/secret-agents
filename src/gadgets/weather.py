import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()


def get_weather(location):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            tz_offset = data["timezone"]
            local_time = datetime.fromtimestamp(data["dt"], tz=timezone(timedelta(seconds=tz_offset)))
            formatted_time = local_time.strftime("%A, %B %d, %Y %I:%M %p")
            return f"Weather in {location}: {weather}, {temperature}°C — {formatted_time} (local time)"
        else:
            return f"Could not retrieve weather for {location}."
    except Exception as e:
        return "Error retrieving weather data."
