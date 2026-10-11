"""
ShwaasShala - FastAPI Application Server
AI Agent and Pediatric Air Quality Advisory System for Indian Schools
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models import AdvisoryRequest, SchoolAdvisory
from app.services.meteo import search_places
from app.services.strands_agent import generate_school_advisory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("shwaasshala.app")

app = FastAPI(
    title="ShwaasShala API",
    description="AI Agent for Indian school outdoor air quality and thermal safety advisories",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Ensure static directory exists
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

PRESET_CITIES = [
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "state": "Delhi NCR", "school": "Delhi Public School, Mathura Rd"},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "state": "Maharashtra", "school": "Bombay Scottish School, Mahim"},
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "school": "National Public School, Indiranagar"},
    {"name": "Hubballi-Dharwad", "lat": 15.3647, "lon": 75.1240, "state": "Karnataka", "school": "KLE English Medium School"},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "state": "West Bengal", "school": "La Martiniere for Boys, Elgin"},
    {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh", "school": "City Montessori School, Gomti Nagar"},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "state": "Maharashtra", "school": "Symbiosis School, Prabhat Rd"},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "state": "Telangana", "school": "Hyderabad Public School, Begumpet"}
]


@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "ShwaasShala API is running. UI index.html not yet initialized."}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ShwaasShala",
        "model_provider": settings.MODEL_PROVIDER,
        "aws_region": settings.AWS_REGION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/presets")
async def get_presets():
    return {"presets": PRESET_CITIES}


@app.get("/api/places")
async def get_places(q: str = Query(..., min_length=2, description="Place or city search query")):
    try:
        results = await search_places(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error querying places: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch location suggestions")


@app.post("/api/advisory", response_model=SchoolAdvisory)
async def create_advisory(req: AdvisoryRequest):
    try:
        advisory = await generate_school_advisory(
            lat=req.lat,
            lon=req.lon,
            place=req.place,
            lang=req.lang
        )
        return advisory
    except Exception as e:
        logger.error(f"Error creating advisory for {req.place}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Advisory calculation failed: {str(e)}")
