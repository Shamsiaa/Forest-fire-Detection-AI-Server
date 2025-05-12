# app/simulation.py

import random
import time
import threading

# Shared state
simulation_state = {
    "running": False,
    "fire_events": []
}

def generate_random_fire_event():
    # Dummy fire coordinates within Turkey's bounding box
    lat = random.uniform(36.0, 42.0)
    lon = random.uniform(26.0, 45.0)
    return {
        "coords": {"latitude": lat, "longitude": lon},
        "class": random.choice(["fire", "smoke"]),
        "confidence": round(random.uniform(0.6, 0.99), 2)
    }

def run_simulation():
    while simulation_state["running"]:
        simulation_state["fire_events"] = [
            generate_random_fire_event() for _ in range(random.randint(1, 5))
        ]
        time.sleep(4)  # simulate every 4 seconds

def start_simulation():
    if not simulation_state["running"]:
        simulation_state["running"] = True
        threading.Thread(target=run_simulation, daemon=True).start()

def stop_simulation():
    simulation_state["running"] = False
    simulation_state["fire_events"] = []
