import pytest
from fastapi.testclient import TestClient
from app.main import app, PRESET_CITIES

client = TestClient(app)

def test_all_eight_preset_cities():
    for city in PRESET_CITIES:
        payload = {
            "lat": city["lat"],
            "lon": city["lon"],
            "place": city["school"],
            "lang": "en"
        }
        res = client.post("/api/advisory", json=payload)
        assert res.status_code == 200, f"Failed for {city['name']}: {res.text}"
        data = res.json()
        assert data["risk_level"] in ["GREEN", "AMBER", "RED"]
        assert data["cpcb_aqi"] >= 0
        assert data["current_pm25"] >= 0
        assert data["safe_window"]["display_label"] is not None
        assert "morning_assembly" in data["activities"]
        assert len(data["parent_whatsapp_message"]) > 0
        print(f"Verified {city['name']}: {data['risk_level']} (AQI: {data['cpcb_aqi']}, PM2.5: {data['current_pm25']})")

def test_static_index_html_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "ShwaasShala" in res.text
    assert "hourlyAqiChart" in res.text
