import time
import threading
import random

from firebase.db_operations import get_random_image_from_location
from .inference import run_detection

# Shared state
simulation_state = {
    "running": False,
    "fire_events": [],
    "seen_images": set()  # Track processed images to avoid duplicates
}

# Locations to fetch images from (all 9 locations)
locations = list(range(1, 10))  # Assuming location IDs are 1 to 9

def generate_fire_event_from_db(location_id=None):
    """Generates a fire event from the given location."""
    # Default to random location if None is passed
    if location_id is None:
        location_id = random.choice(locations)
    
    data = get_random_image_from_location(location_id)
    if not data or "image" not in data:
        return None

    filename = data["original_data"].get("filename")
    if filename in simulation_state["seen_images"]:
        print(f"⏩ Skipping already seen image: {filename}")
        return None  # Skip if this image has already been processed

    # Add image filename to seen images to prevent reprocessing
    simulation_state["seen_images"].add(filename)

    detection_result = run_detection(data["image"])
    for det in detection_result["detections"]:
        if det["class"] in ["fire", "smoke"]:
            return {
                "coords": {
                    "latitude": data["latitude"],
                    "longitude": data["longitude"]
                },
                "class": det["class"],
                "confidence": det["confidence"],
                "filename": filename,
                "timestamp": data["original_data"].get("timestamp"),
                "image_url": data["original_data"].get("image_url")
            }
    return None

def run_simulation():
    """Runs the simulation and generates fire events periodically."""
    while simulation_state["running"]:
        events = []
        
        # Fetch random images from all locations and process them
        for _ in range(random.randint(1, 3)):  # Fetch 1 to 3 detections per round
            # Fetch image from random location
            event = generate_fire_event_from_db(location_id=None)
            if event:
                events.append(event)

            # Add a small delay between processing each image
            time.sleep(4)  # Adjust delay as necessary (2 seconds here for example)

        # Update fire events state with the new detections
        simulation_state["fire_events"] = events
        time.sleep(5)  # Delay between cycles to allow map updates (5 seconds)

def start_simulation():
    """Starts the simulation in a background thread."""
    if not simulation_state["running"]:
        simulation_state["running"] = True
        simulation_state["seen_images"] = set()  # Reset image history on start
        threading.Thread(target=run_simulation, daemon=True).start()
        print("🟢 Simulation started in background")

def stop_simulation():
    """Stops the simulation and resets the state."""
    simulation_state["running"] = False
    simulation_state["fire_events"] = []
    simulation_state["seen_images"] = set()  # Reset processed image history
    print("🛑 Simulation stopped and state reset")
