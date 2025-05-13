from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .simulation import start_simulation, stop_simulation, simulation_state
from .alerts import router as alerts_router  # Direct import from same directory

app = FastAPI()

# Allow all CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-simulation")
def start_simulation_endpoint(background_tasks: BackgroundTasks):
    print("📡 /start-simulation called")
    if not simulation_state["running"]:
        background_tasks.add_task(start_simulation)
        print("🟢 Simulation started in background")
        return {"status": "started"}
    print("⚠️ Simulation already running")
    return {"status": "already running"}

@app.post("/stop-simulation")
def stop_simulation_endpoint():
    print("🛑 /stop-simulation called — stopping simulation")
    stop_simulation()
    return {"status": "stopped"}

@app.get("/fire-events")
def get_current_detections():
    print("📍 /fire-events called — returning current detections")

    fire_events = simulation_state.get("fire_events", [])
    formatted_events = []

    for event in fire_events:
        coords = event.get("coords", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")

        # Validate latitude/longitude
        if lat is None or lon is None:
            continue

        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue

        formatted_events.append({
            "coords": {
                "latitude": lat,
                "longitude": lon
            },
            "image_url": event.get("image_url"),
            "forest_name": event.get("forest_name"),
            "class": event.get("class"),
            "confidence": event.get("confidence", 0)
        })

    return formatted_events

# Include alert routes with prefix
app.include_router(alerts_router, prefix="/alerts", tags=["alerts"])