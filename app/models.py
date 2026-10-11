from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class CPCBQualityBand(str, Enum):
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    MODERATE = "Moderate"
    POOR = "Poor"
    VERY_POOR = "Very Poor"
    SEVERE = "Severe"

class RiskLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"

class ActivityItem(BaseModel):
    status: str = Field(description="One of: Safe, Allowed, Caution, Restricted, Cancelled, Move Indoors, N95 Essential")
    detail: str = Field(description="Clear, actionable instructions for school coordinator")

class ActivityGuidance(BaseModel):
    morning_assembly: ActivityItem
    sports_pe: ActivityItem
    outdoor_lunch: ActivityItem
    commute: ActivityItem
    sensitive_kids: ActivityItem

class SafeWindow(BaseModel):
    start_time: str = Field(description="Start time (e.g., '10:00 AM' or '2026-10-12T10:00')")
    end_time: str = Field(description="End time (e.g., '12:00 PM' or '2026-10-12T12:00')")
    display_label: str = Field(description="Human readable label, e.g., 'Today 10:00 AM - 12:00 PM'")
    avg_pm25: float = Field(description="Average PM2.5 in µg/m³ during this window")
    avg_temp: float = Field(description="Average apparent temperature in °C during this window")
    cpcb_band: str = Field(description="CPCB band during this window")
    recommendation: str = Field(description="Recommendation for outdoor exposure")

class HourlyDataPoint(BaseModel):
    time: str
    pm2_5: float
    pm10: Optional[float] = None
    us_aqi: Optional[int] = None
    cpcb_aqi: int
    cpcb_band: str
    temperature: float
    apparent_temperature: float
    is_safe_window: bool = False

class AdvisoryRequest(BaseModel):
    lat: float
    lon: float
    place: str
    lang: str = "en"  # "en", "hi", "kn"

class SchoolAdvisory(BaseModel):
    place: str
    timestamp: str
    risk_level: RiskLevel
    one_line_verdict: str
    current_pm25: float
    current_pm10: float
    cpcb_aqi: int
    cpcb_band: str
    current_temperature: float
    apparent_temperature: float
    heat_risk: str
    safe_window: SafeWindow
    activities: ActivityGuidance
    parent_whatsapp_message: str
    language: str
    engine: str = "ai_strands"  # "ai_strands" or "rule_fallback"
    engine_label: str = "⚡ AI-generated (Strands Agent)"
    hourly_forecast: List[HourlyDataPoint] = []
