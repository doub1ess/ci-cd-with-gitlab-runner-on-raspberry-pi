# test_api.py
import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_weather_ok(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake-key")
    monkeypatch.setenv("CITY", "Пермь")

    class Resp:
        status_code = 200

        def json(self):
            # Минимально реалистичный ответ OpenWeather: есть name, main.temp и weather[]
            # В реальном API weather — массив объектов. [web:187]
            return {
                "name": "Пермь",
                "main": {"temp": -5},
                "weather": [
                    {
                        "id": 600,
                        "main": "Snow",
                        "description": "небольшой снег",
                        "icon": "13n",
                    }
                ],
            }

    def fake_get(url, params=None, timeout=None):
        assert url == "https://api.openweathermap.org/data/2.5/weather"
        assert params["q"] == "Пермь"
        assert params["appid"] == "fake-key"
        assert params["units"] == "metric"
        assert params["lang"] == "ru"
        assert timeout == 10
        return Resp()

    monkeypatch.setattr(main.requests, "get", fake_get)

    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {
        "city": "Пермь",
        "temp": -5,
        "weather": {
            "id": 600,
            "main": "Snow",
            "description": "небольшой снег",
            "icon": "13n",
        },
    }


def test_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    monkeypatch.setenv("CITY", "Пермь")

    r = client.get("/")
    assert r.status_code == 500
    assert r.json()["detail"] == "OPENWEATHER_API_KEY is not set"


def test_no_city(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake-key")
    monkeypatch.delenv("CITY", raising=False)

    r = client.get("/")
    assert r.status_code == 500
    assert r.json()["detail"] == "CITY is not set"


def test_openweather_failed(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake-key")
    monkeypatch.setenv("CITY", "Пермь")

    class Resp:
        status_code = 401

        def json(self):
            return {"message": "invalid api key"}

    def fake_get(url, params=None, timeout=None):
        return Resp()

    monkeypatch.setattr(main.requests, "get", fake_get)

    r = client.get("/")
    assert r.status_code == 502
    assert r.json()["detail"] == "OpenWeather request failed"
