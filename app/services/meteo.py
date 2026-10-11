"""
Open-Meteo API Client with caching, retries, and timeouts.
Pulls free air quality, weather forecast, and geocoding data without requiring API keys.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from app.cache import cache

logger = logging.getLogger("shwaasshala.meteo")

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Timeout settings: 10s connect, 15s read
TIMEOUT = httpx.Timeout(15.0, connect=10.0)
RETRIES = 2


async def fetch_with_retry(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            last_err = e
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
    raise RuntimeError(f"Failed to fetch data from {url} after {RETRIES + 1} attempts: {last_err}")


def fetch_with_retry_sync(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            with httpx.Client(timeout=TIMEOUT) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            last_err = e
            logger.warning(f"Sync attempt {attempt + 1} failed for {url}: {e}")
    raise RuntimeError(f"Failed to fetch data from {url} after {RETRIES + 1} attempts: {last_err}")


async def get_air_quality(lat: float, lon: float) -> Dict[str, Any]:
    cache_key = f"aq_{round(lat, 3)}_{round(lon, 3)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "hourly": "pm2_5,pm10,us_aqi",
        "timezone": "auto",
        "forecast_days": 2
    }
    data = await fetch_with_retry(AIR_QUALITY_URL, params)
    cache.set(cache_key, data, ttl=600)
    return data


def get_air_quality_sync(lat: float, lon: float) -> Dict[str, Any]:
    cache_key = f"aq_{round(lat, 3)}_{round(lon, 3)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "hourly": "pm2_5,pm10,us_aqi",
        "timezone": "auto",
        "forecast_days": 2
    }
    data = fetch_with_retry_sync(AIR_QUALITY_URL, params)
    cache.set(cache_key, data, ttl=600)
    return data


async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    cache_key = f"weather_{round(lat, 3)}_{round(lon, 3)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code",
        "timezone": "auto",
        "forecast_days": 2
    }
    data = await fetch_with_retry(WEATHER_FORECAST_URL, params)
    cache.set(cache_key, data, ttl=600)
    return data


def get_weather_sync(lat: float, lon: float) -> Dict[str, Any]:
    cache_key = f"weather_{round(lat, 3)}_{round(lon, 3)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code",
        "timezone": "auto",
        "forecast_days": 2
    }
    data = fetch_with_retry_sync(WEATHER_FORECAST_URL, params)
    cache.set(cache_key, data, ttl=600)
    return data


async def search_places(query: str) -> List[Dict[str, Any]]:
    query = query.strip()
    if not query:
        return []

    cache_key = f"geo_{query.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "name": query,
        "count": 6,
        "language": "en",
        "format": "json"
    }
    try:
        data = await fetch_with_retry(GEOCODING_URL, params)
        results = []
        for item in data.get("results", []):
            country = item.get("country", "")
            admin1 = item.get("admin1", "")
            name = item.get("name", "")
            label_parts = [name]
            if admin1 and admin1 != name:
                label_parts.append(admin1)
            if country:
                label_parts.append(country)
            
            results.append({
                "name": name,
                "label": ", ".join(label_parts),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "country": country,
                "admin1": admin1
            })
        cache.set(cache_key, results, ttl=1800)
        return results
    except Exception as e:
        logger.error(f"Geocoding search failed: {e}")
        return []
