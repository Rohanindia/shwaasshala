import pytest
from fastapi.testclient import TestClient
from app.main import app, PRESET_CITIES

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ShwaasShala"
    assert "model_provider" in data

def test_presets_list():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert len(data["presets"]) == 8
    names = [p["name"] for p in data["presets"]]
    assert "Delhi" in names
    assert "Hubballi-Dharwad" in names
    assert "Bengaluru" in names

def test_places_search():
    response = client.get("/api/places?q=Delhi")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

def test_advisory_endpoint_preset_cities():
    # Test Delhi in English
    payload = {
        "lat": 28.6139,
        "lon": 77.2090,
        "place": "Delhi Public School",
        "lang": "en"
    }
    response = client.post("/api/advisory", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["place"] == "Delhi Public School"
    assert data["risk_level"] in ["GREEN", "AMBER", "RED"]
    assert "cpcb_aqi" in data
    assert "safe_window" in data
    assert "activities" in data
    assert len(data["hourly_forecast"]) > 0
    assert "parent_whatsapp_message" in data
    assert "engine_label" in data

def test_advisory_endpoint_hindi_and_kannada():
    # Test Bengaluru in Kannada
    payload_kn = {
        "lat": 12.9716,
        "lon": 77.5946,
        "place": "Bengaluru Central School",
        "lang": "kn"
    }
    response_kn = client.post("/api/advisory", json=payload_kn)
    assert response_kn.status_code == 200
    data_kn = response_kn.json()
    assert data_kn["language"] == "kn"
    assert "ಶ್ವಾಸಶಾಲಾ" in data_kn["parent_whatsapp_message"]

    # Test Lucknow in Hindi
    payload_hi = {
        "lat": 26.8467,
        "lon": 80.9462,
        "place": "City Montessori School, Lucknow",
        "lang": "hi"
    }
    response_hi = client.post("/api/advisory", json=payload_hi)
    assert response_hi.status_code == 200
    data_hi = response_hi.json()
    assert data_hi["language"] == "hi"
    assert "श्वासशाला" in data_hi["parent_whatsapp_message"]
