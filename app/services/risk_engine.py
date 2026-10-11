"""
Deterministic Risk Engine for ShwaasShala.
Maps PM2.5 to CPCB India AQI standards, computes thermal stress,
determines overall school risk level (GREEN / AMBER / RED),
and finds the optimal 2-hour outdoor window.
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.models import (
    CPCBQualityBand,
    RiskLevel,
    ActivityGuidance,
    ActivityItem,
    SafeWindow,
    HourlyDataPoint,
    SchoolAdvisory
)
from app.services.templates import get_whatsapp_message


def compute_cpcb_aqi(pm25: float) -> Tuple[int, CPCBQualityBand]:
    """
    Computes Indian CPCB sub-index for PM2.5 (24h µg/m³ breakpoints)
    0-30: Good (0-50)
    31-60: Satisfactory (51-100)
    61-90: Moderate (101-200)
    91-120: Poor (201-300)
    121-250: Very Poor (301-400)
    250+: Severe (401-500)
    """
    val = max(0.0, float(pm25))
    
    if val <= 30.0:
        aqi = round((50.0 / 30.0) * val)
        return aqi, CPCBQualityBand.GOOD
    elif val <= 60.0:
        aqi = round(51.0 + ((100.0 - 51.0) / (60.0 - 31.0)) * (val - 31.0))
        return aqi, CPCBQualityBand.SATISFACTORY
    elif val <= 90.0:
        aqi = round(101.0 + ((200.0 - 101.0) / (90.0 - 61.0)) * (val - 61.0))
        return aqi, CPCBQualityBand.MODERATE
    elif val <= 120.0:
        aqi = round(201.0 + ((300.0 - 201.0) / (120.0 - 91.0)) * (val - 91.0))
        return aqi, CPCBQualityBand.POOR
    elif val <= 250.0:
        aqi = round(301.0 + ((400.0 - 301.0) / (250.0 - 121.0)) * (val - 121.0))
        return aqi, CPCBQualityBand.VERY_POOR
    else:
        # Severe: 250 - 380 ug/m3 maps to 401 - 500
        if val >= 380.0:
            aqi = 500
        else:
            aqi = round(401.0 + ((500.0 - 401.0) / (380.0 - 251.0)) * (val - 251.0))
        return min(500, aqi), CPCBQualityBand.SEVERE


def assess_heat_risk(apparent_temp: float) -> str:
    """
    Evaluates apparent temperature for school children thermal safety.
    """
    temp = float(apparent_temp)
    if temp >= 42.0:
        return "Extreme Heat (Heat Stroke Risk)"
    elif temp >= 38.0:
        return "High Heat (Thermal Discomfort)"
    elif temp >= 32.0:
        return "Moderate Heat (Hydration Needed)"
    else:
        return "Comfortable"


def determine_school_risk(pm25: float, apparent_temp: float) -> Tuple[RiskLevel, str]:
    """
    Deterministically computes school risk verdict (GREEN / AMBER / RED)
    combining CPCB AQI band and apparent temperature.
    """
    _, band = compute_cpcb_aqi(pm25)
    temp = float(apparent_temp)

    # 1. Extreme Heat overrides to RED immediately
    if temp >= 42.0:
        return RiskLevel.RED, "Extreme heat hazard (>=42°C). Cancel outdoor sports and assembly."

    # 2. Air quality band evaluation
    if band in [CPCBQualityBand.POOR, CPCBQualityBand.VERY_POOR, CPCBQualityBand.SEVERE]:
        return RiskLevel.RED, f"Unsafe air quality ({band.value} band). Cancel outdoor morning assembly & sports."

    if band == CPCBQualityBand.MODERATE:
        if temp >= 38.0:
            return RiskLevel.RED, "Moderate pollution combined with high heat index creates hazardous outdoor conditions."
        return RiskLevel.AMBER, "Moderate air quality. Limit strenuous outdoor exertion; sensitive kids stay indoors."

    # Good or Satisfactory
    if temp >= 38.0:
        return RiskLevel.AMBER, "Air quality is good but high thermal heat requires limiting outdoor physical exertion."

    return RiskLevel.GREEN, "Air quality and thermal conditions are safe for outdoor assembly, sports, and recess."


def format_window_label(dt_start: datetime, dt_end: datetime) -> str:
    start_str = dt_start.strftime("%I:%M %p").lstrip("0")
    end_str = dt_end.strftime("%I:%M %p").lstrip("0")
    day_label = dt_start.strftime("%a %b %d")
    return f"{day_label}, {start_str} - {end_str}"


def find_safe_window(
    hourly_times: List[str],
    hourly_pm25: List[float],
    hourly_temp: List[float]
) -> Tuple[SafeWindow, List[int]]:
    """
    Finds the optimal 2-hour continuous window in the next 48 hours.
    Prioritizes daylight / school hours (07:00 to 17:00).
    Returns (SafeWindow, [safe_hour_index1, safe_hour_index2]).
    """
    if not hourly_times or len(hourly_times) < 2:
        return SafeWindow(
            start_time="09:00",
            end_time="11:00",
            display_label="09:00 AM - 11:00 AM",
            avg_pm25=30.0,
            avg_temp=25.0,
            cpcb_band="Good",
            recommendation="Default safe outdoor window"
        ), []

    best_idx = 0
    best_score = float("inf")
    
    # First pass: check school daytime hours (07:00 to 17:00)
    daytime_candidates = []
    all_candidates = []

    for i in range(len(hourly_times) - 1):
        try:
            dt1 = datetime.fromisoformat(hourly_times[i])
            hour = dt1.hour
        except Exception:
            hour = 10

        p1 = hourly_pm25[i] if i < len(hourly_pm25) else 50.0
        p2 = hourly_pm25[i+1] if (i+1) < len(hourly_pm25) else 50.0
        avg_pm = (p1 + p2) / 2.0

        t1 = hourly_temp[i] if i < len(hourly_temp) else 28.0
        t2 = hourly_temp[i+1] if (i+1) < len(hourly_temp) else 28.0
        avg_t = (t1 + t2) / 2.0

        # Score function: PM2.5 + penalty for high heat (>32°C)
        heat_penalty = max(0.0, (avg_t - 32.0) * 3.0)
        score = avg_pm + heat_penalty

        all_candidates.append((score, i, avg_pm, avg_t))
        if 7 <= hour <= 16:
            daytime_candidates.append((score, i, avg_pm, avg_t))

    candidates = daytime_candidates if daytime_candidates else all_candidates
    candidates.sort(key=lambda x: x[0])
    
    selected_score, sel_idx, sel_pm, sel_temp = candidates[0]
    
    try:
        dt_start = datetime.fromisoformat(hourly_times[sel_idx])
        dt_end = datetime.fromisoformat(hourly_times[sel_idx + 1])
        display_label = format_window_label(dt_start, dt_end)
        s_time = dt_start.strftime("%H:%M")
        e_time = dt_end.strftime("%H:%M")
    except Exception:
        display_label = f"Hour {sel_idx}:00 - {sel_idx+2}:00"
        s_time = f"{sel_idx}:00"
        e_time = f"{sel_idx+2}:00"

    _, band = compute_cpcb_aqi(sel_pm)
    
    if band in [CPCBQualityBand.GOOD, CPCBQualityBand.SATISFACTORY]:
        rec = f"Ideal for outdoor sports and free play (Avg PM2.5: {sel_pm:.1f} µg/m³)."
    elif band == CPCBQualityBand.MODERATE:
        rec = f"Acceptable for light outdoor activities with hydration (Avg PM2.5: {sel_pm:.1f} µg/m³)."
    else:
        rec = f"Lowest pollution interval in 48h, but still high ({sel_pm:.1f} µg/m³). Limit exposure."

    safe_win = SafeWindow(
        start_time=s_time,
        end_time=e_time,
        display_label=display_label,
        avg_pm25=round(sel_pm, 1),
        avg_temp=round(sel_temp, 1),
        cpcb_band=band.value,
        recommendation=rec
    )
    return safe_win, [sel_idx, sel_idx + 1]


def build_activity_guidance(risk: RiskLevel, band: CPCBQualityBand, heat: str) -> ActivityGuidance:
    if risk == RiskLevel.GREEN:
        return ActivityGuidance(
            morning_assembly=ActivityItem(
                status="Safe",
                detail="Full outdoor assembly permitted. Excellent air quality for student gatherings."
            ),
            sports_pe=ActivityItem(
                status="Safe",
                detail="Normal outdoor sports and physical training encouraged."
            ),
            outdoor_lunch=ActivityItem(
                status="Allowed",
                detail="Students can safely eat lunch and play in open courtyards."
            ),
            commute=ActivityItem(
                status="Normal",
                detail="Standard commute. No masks required."
            ),
            sensitive_kids=ActivityItem(
                status="Normal",
                detail="No special restrictions. Children with mild asthma can participate normally."
            )
        )
    elif risk == RiskLevel.AMBER:
        return ActivityGuidance(
            morning_assembly=ActivityItem(
                status="Caution",
                detail="Keep assembly under 15 minutes or conduct in shaded, well-ventilated areas."
            ),
            sports_pe=ActivityItem(
                status="Light Only",
                detail="Replace heavy endurance drills with light skill practice or indoor yoga."
            ),
            outdoor_lunch=ActivityItem(
                status="Restricted",
                detail="Permitted in shaded areas. Avoid strenuous chasing or running games."
            ),
            commute=ActivityItem(
                status="Mask Recommended",
                detail="Children traveling via open auto-rickshaws or walking should wear masks."
            ),
            sensitive_kids=ActivityItem(
                status="Caution",
                detail="Asthmatic and sensitive children must remain in indoor classrooms; keep inhalers ready."
            )
        )
    else:  # RED
        return ActivityGuidance(
            morning_assembly=ActivityItem(
                status="Cancelled",
                detail="Outdoor assembly cancelled. Broadcast announcements via classroom PA system."
            ),
            sports_pe=ActivityItem(
                status="Move Indoors",
                detail="All outdoor PE suspended. Move classes indoors to library or multipurpose hall."
            ),
            outdoor_lunch=ActivityItem(
                status="Indoors Only",
                detail="Mandatory indoor lunch and recess. Keep classroom doors and windows shut."
            ),
            commute=ActivityItem(
                status="N95 Essential",
                detail="All students and staff should wear N95/well-fitted masks during travel to school."
            ),
            sensitive_kids=ActivityItem(
                status="Strictly Indoors",
                detail="High alert: Asthmatic students must stay indoors in air-filtered rooms with inhalers accessible."
            )
        )


def generate_deterministic_advisory(
    place: str,
    timestamp: str,
    current_pm25: float,
    current_pm10: float,
    current_temp: float,
    apparent_temp: float,
    hourly_times: List[str],
    hourly_pm25: List[float],
    hourly_pm10: List[float],
    hourly_temp: List[float],
    hourly_apparent_temp: List[float],
    hourly_us_aqi: List[int],
    lang: str = "en"
) -> SchoolAdvisory:
    """
    Creates the complete deterministic advisory object (Rule-Based Fallback).
    Ensures the demo NEVER breaks even without LLM credentials.
    """
    cpcb_aqi, band = compute_cpcb_aqi(current_pm25)
    heat_label = assess_heat_risk(apparent_temp)
    risk_level, verdict = determine_school_risk(current_pm25, apparent_temp)
    
    safe_window, safe_indices = find_safe_window(hourly_times, hourly_pm25, hourly_apparent_temp)
    activities = build_activity_guidance(risk_level, band, heat_label)
    
    wa_message = get_whatsapp_message(
        risk_level=risk_level.value,
        place=place,
        cpcb_band=band.value,
        cpcb_aqi=cpcb_aqi,
        safe_window=safe_window.display_label,
        lang=lang
    )

    # Build 48h forecast records
    forecast_points: List[HourlyDataPoint] = []
    safe_set = set(safe_indices)
    
    for idx, t in enumerate(hourly_times[:48]):
        p25 = hourly_pm25[idx] if idx < len(hourly_pm25) else current_pm25
        p10 = hourly_pm10[idx] if idx < len(hourly_pm10) else None
        u_aqi = hourly_us_aqi[idx] if idx < len(hourly_us_aqi) else None
        t_val = hourly_temp[idx] if idx < len(hourly_temp) else current_temp
        app_t = hourly_apparent_temp[idx] if idx < len(hourly_apparent_temp) else apparent_temp
        h_aqi, h_band = compute_cpcb_aqi(p25)
        
        forecast_points.append(
            HourlyDataPoint(
                time=t,
                pm2_5=round(p25, 1),
                pm10=round(p10, 1) if p10 is not None else None,
                us_aqi=u_aqi,
                cpcb_aqi=h_aqi,
                cpcb_band=h_band.value,
                temperature=round(t_val, 1),
                apparent_temperature=round(app_t, 1),
                is_safe_window=(idx in safe_set)
            )
        )

    return SchoolAdvisory(
        place=place,
        timestamp=timestamp,
        risk_level=risk_level,
        one_line_verdict=verdict,
        current_pm25=round(current_pm25, 1),
        current_pm10=round(current_pm10, 1),
        cpcb_aqi=cpcb_aqi,
        cpcb_band=band.value,
        current_temperature=round(current_temp, 1),
        apparent_temperature=round(apparent_temp, 1),
        heat_risk=heat_label,
        safe_window=safe_window,
        activities=activities,
        parent_whatsapp_message=wa_message,
        language=lang,
        engine="rule_fallback",
        engine_label="🛡️ Rule-based Fallback (Deterministic Engine)",
        hourly_forecast=forecast_points
    )
