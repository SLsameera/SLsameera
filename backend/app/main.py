from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

from app.domain.astro.moon import MoonOrbitSimulator

app = FastAPI(title="Pivisuma Backend API")

# Basic CORS for local dev; adjust via env in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = MoonOrbitSimulator()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/astro/moon")
def get_moon(dt: Optional[str] = Query(default=None, description="ISO8601 datetime (UTC). If omitted, uses current UTC.")):
    if dt:
        observation_time = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    else:
        observation_time = datetime.utcnow()

    x, y, z = simulator.get_moon_position(observation_time)
    tidal_force = simulator.estimate_tidal_force(observation_time)
    return {
        "datetime_utc": observation_time.isoformat(),
        "position_km": {"x": x, "y": y, "z": z},
        "tidal_force_normalized": tidal_force,
    }