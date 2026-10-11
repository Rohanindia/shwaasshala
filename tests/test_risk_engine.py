import pytest
from datetime import datetime
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
    # --- Rule 2 Test: Exactly 2 consecutive hours (e.g. 10:00 AM - 12:00 PM) ---
    times_r2 = [
        "2026-10-12T07:00",
        "2026-10-12T08:00",
        "2026-10-12T09:00",
        "2026-10-12T10:00",
        "2026-10-12T11:00",
        "2026-10-12T12:00"
    ]
    # At 10:00 and 11:00 PM2.5 is cleanest (25 and 27)
    pm25_r2 = [180.0, 150.0, 120.0, 25.0, 27.0, 95.0]
    temps_r2 = [24.0, 25.0, 27.0, 28.0, 29.0, 31.0]

    window, indices = find_safe_window(
        times_r2, pm25_r2, temps_r2,
        current_time=datetime(2026, 10, 12, 7, 0)
    )
    assert indices == [3, 4]  # 2 consecutive hours
    assert window.start_time == "10:00"
    assert window.end_time == "12:00"  # start + 2h
    assert "10:00 AM - 12:00 PM" in window.display_label
    assert window.avg_pm25 == 26.0  # (25.0 + 27.0) / 2
    assert window.avg_temp == 28.5  # (28.0 + 29.0) / 2
    assert window.cpcb_band == "Good"

    # --- Rule 1 Test: Only hours >= current hour, never already started or passed ---
    times_r1 = [
        "2026-10-12T08:00",
        "2026-10-12T09:00",
        "2026-10-12T10:00",
        "2026-10-12T11:00",
        "2026-10-12T12:00",
        "2026-10-12T13:00",
        "2026-10-12T14:00"
    ]
    # Clean morning (10.0 at 08:00), but now is 11:30 AM. Cleanest remaining is 12:00-14:00 (35.0, 35.0).
    pm25_r1 = [10.0, 10.0, 10.0, 80.0, 35.0, 35.0, 70.0]
    temps_r1 = [25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0]

    now_1130 = datetime(2026, 10, 12, 11, 30)
    window_r1, indices_r1 = find_safe_window(times_r1, pm25_r1, temps_r1, current_time=now_1130)
    # The 08:00 and 10:00 windows have passed, so candidate start hours must be >= 11:30
    assert indices_r1 == [4, 5]  # 12:00 and 13:00 (12:00 PM - 2:00 PM)
    assert window_r1.start_time == "12:00"
    assert window_r1.end_time == "14:00"
    assert "12:00 PM - 2:00 PM" in window_r1.display_label
    assert window_r1.avg_pm25 == 35.0

    # --- Rule 3 Test: School daylight 6 AM - 6 PM; if none remain today, use tomorrow's ---
    times_r3 = [
        # Today evening & night
        "2026-10-12T19:00", "2026-10-12T20:00", "2026-10-12T21:00", "2026-10-12T22:00", "2026-10-12T23:00",
        # Tomorrow morning & daytime
        "2026-10-13T00:00", "2026-10-13T02:00",  # Night (must not be picked even if super clean)
        "2026-10-13T06:00", "2026-10-13T07:00", "2026-10-13T08:00",
        "2026-10-13T09:00", "2026-10-13T10:00", "2026-10-13T11:00", "2026-10-13T12:00"
    ]
    pm25_r3 = [
        120.0, 130.0, 140.0, 150.0, 160.0,  # Today evening
        5.0, 5.0,                            # Tomorrow 00:00 and 02:00 night (excluded by 6 AM rule)
        90.0, 80.0, 70.0,                   # Tomorrow 06:00-08:00
        20.0, 22.0, 24.0, 90.0              # Tomorrow 09:00-11:00 (cleanest daylight window)
    ]
    temps_r3 = [25.0] * len(times_r3)

    now_evening = datetime(2026, 10, 12, 19, 30)
    window_r3, indices_r3 = find_safe_window(times_r3, pm25_r3, temps_r3, current_time=now_evening)
    # Nighttime 00:00 & 02:00 (pm25=5.0) are NOT picked because of 6 AM daylight restriction
    # Today evening has no daylight left, so tomorrow's daylight is selected
    assert "Oct 13" in window_r3.display_label
    assert window_r3.start_time == "09:00"
    assert window_r3.end_time == "11:00"
    assert "9:00 AM - 11:00 AM" in window_r3.display_label
    assert window_r3.avg_pm25 == 21.0

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
