import pytest
from app.services.risk_engine import (
    compute_cpcb_aqi,
    assess_heat_risk,
    determine_school_risk,
    find_safe_window,
    CPCBQualityBand,
    RiskLevel
)
from app.services.templates import get_whatsapp_message

def test_cpcb_aqi_breakpoints():
    # Good band: 0 - 30 -> 0 - 50
    aqi, band = compute_cpcb_aqi(15.0)
    assert band == CPCBQualityBand.GOOD
    assert aqi == 25

    # Satisfactory band: 31 - 60 -> 51 - 100
    aqi, band = compute_cpcb_aqi(45.5)
    assert band == CPCBQualityBand.SATISFACTORY
    assert 51 <= aqi <= 100

    # Moderate band: 61 - 90 -> 101 - 200
    aqi, band = compute_cpcb_aqi(75.0)
    assert band == CPCBQualityBand.MODERATE
    assert 101 <= aqi <= 200

    # Poor band: 91 - 120 -> 201 - 300
    aqi, band = compute_cpcb_aqi(105.0)
    assert band == CPCBQualityBand.POOR
    assert 201 <= aqi <= 300

    # Very Poor band: 121 - 250 -> 301 - 400
    aqi, band = compute_cpcb_aqi(180.0)
    assert band == CPCBQualityBand.VERY_POOR
    assert 301 <= aqi <= 400

    # Severe band: > 250 -> 401 - 500
    aqi, band = compute_cpcb_aqi(320.0)
    assert band == CPCBQualityBand.SEVERE
    assert aqi > 400

    # Severe cap at extreme PM2.5
    aqi, band = compute_cpcb_aqi(450.0)
    assert band == CPCBQualityBand.SEVERE
    assert aqi == 500

def test_heat_risk_evaluation():
    assert assess_heat_risk(25.0) == "Comfortable"
    assert "Moderate Heat" in assess_heat_risk(34.0)
    assert "High Heat" in assess_heat_risk(39.0)
    assert "Extreme Heat" in assess_heat_risk(43.5)

def test_school_risk_matrix():
    # Clean air + comfortable temp = GREEN
    risk, _ = determine_school_risk(20.0, 26.0)
    assert risk == RiskLevel.GREEN

    # Moderate air = AMBER
    risk, _ = determine_school_risk(75.0, 28.0)
    assert risk == RiskLevel.AMBER

    # Good air but high heat = AMBER
    risk, _ = determine_school_risk(25.0, 39.5)
    assert risk == RiskLevel.AMBER

    # Poor air = RED
    risk, _ = determine_school_risk(110.0, 25.0)
    assert risk == RiskLevel.RED

    # Severe air = RED
    risk, _ = determine_school_risk(280.0, 22.0)
    assert risk == RiskLevel.RED

    # Extreme heat (>= 42 C) overrides to RED regardless of clean air
    risk, _ = determine_school_risk(15.0, 42.5)
    assert risk == RiskLevel.RED

def test_find_safe_window():
    times = [
        "2026-10-12T07:00",
        "2026-10-12T08:00",
        "2026-10-12T09:00",
        "2026-10-12T10:00",
        "2026-10-12T11:00",
        "2026-10-12T12:00"
    ]
    # Hourly PM2.5: morning is dirty (150), 10:00-12:00 is clean (25)
    pm25 = [180.0, 150.0, 120.0, 25.0, 28.0, 95.0]
    temps = [24.0, 25.0, 27.0, 28.0, 29.0, 31.0]

    window, indices = find_safe_window(times, pm25, temps)
    assert indices == [3, 4]  # 10:00 and 11:00 window
    assert window.avg_pm25 == 26.5
    assert window.cpcb_band == "Good"

def test_whatsapp_messages_length():
    for lang in ["en", "hi", "kn"]:
        for risk in ["GREEN", "AMBER", "RED"]:
            msg = get_whatsapp_message(
                risk_level=risk,
                place="Delhi Public School",
                cpcb_band="Poor",
                cpcb_aqi=240,
                safe_window="10:00 AM - 12:00 PM",
                lang=lang
            )
            # Count words
            word_count = len(msg.split())
            assert word_count <= 60, f"Language {lang} for {risk} exceeded 60 words: {word_count}"
