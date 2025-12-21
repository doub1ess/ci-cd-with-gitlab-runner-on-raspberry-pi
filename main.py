import os
import requests
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
def root():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = os.getenv("CITY")

    if not api_key:
        raise HTTPException(status_code=500, detail="OPENWEATHER_API_KEY is not set")
    if not city:
        raise HTTPException(status_code=500, detail="CITY is not set")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru",
    }

    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="OpenWeather request failed")

    data = r.json()
    w0 = (data.get("weather") or [{}])[0]  # первый элемент массива weather

    return {
        "city": data.get("name", city),
        "temp": data.get("main", {}).get("temp"),
        "weather": {
            "id": w0.get("id"),
            "main": w0.get("main"),
            "description": w0.get("description"),
            "icon": w0.get("icon"),
        },
}
    # return {
    #     "city": data.get("name", city),
    #     "temp": data.get("main", {}).get("temp"),

    # }

