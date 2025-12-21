import os
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def test_weather_ok(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "fake-key")
    monkeypatch.setenv("CITY", "Пермь")

    class Resp:
        status_code = 200
        def json(self):
            return {"name": "Пермь", "main": {"temp": -5}}

    def fake_get(url, params=None, timeout=None):
        # минимальная проверка, что параметры реально прокинулись
        assert params["q"] == "Пермь"
        assert params["appid"] == "fake-key"
        assert params["units"] == "metric"
        assert params["lang"] == "ru"
        return Resp()

    monkeypatch.setattr(main.requests, "get", fake_get)

    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"city": "Пермь", "temp": -5}

def test_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    r = client.get("/")
    assert r.status_code == 500

