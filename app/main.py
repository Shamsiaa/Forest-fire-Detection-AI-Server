from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.simulation import start_simulation, stop_simulation, simulation_state

app = FastAPI()

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
    from app.simulation import simulation_state
    return simulation_state["fire_events"]
