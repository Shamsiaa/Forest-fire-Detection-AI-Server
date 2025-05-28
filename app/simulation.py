import time
import threading
import asyncio
import random
from datetime import datetime
from firebase.db_operations import get_valid_images_from_location, load_image_from_url
from .inference import run_detection
from firebase.config import db
from threading import Lock

# Add thread lock for safe state updates
simulation_lock = Lock()

simulation_state = {
    "running": False,
    "fire_events": [],
    "thread": None  # Track the simulation thread
}

MAX_DETECTIONS = 4  # Maximum 4 detections total
DETECTION_DELAY = 2  # Delay between detections

async def simulate_fire_detection():
    with simulation_lock:
        simulation_state["running"] = True
        simulation_state["fire_events"] = []  # Reset previous fire events

    try:
        # Get all forest locations
        location_docs = db.collection("forestLocations").stream()
        forest_locations = [doc.id for doc in location_docs]
        random.shuffle(forest_locations)  # Randomize the order

        total_detected = 0
        used_locations = set()  # Track which locations we've already used

        while total_detected < MAX_DETECTIONS:
            with simulation_lock:
                if not simulation_state["running"]:
                    break

            # Find next available location we haven't used yet
            location_id = None
            for loc_id in forest_locations:
                if loc_id not in used_locations:
                    location_id = loc_id
                    break
            
            if location_id is None:
                print("⚠️ No more unique forest locations available")
                break

            valid_images = get_valid_images_from_location(location_id)
            if not valid_images:
                used_locations.add(location_id)
                continue

            # Take one random image from this location
            image_data = random.choice(valid_images)
            used_locations.add(location_id)

            image = load_image_from_url(image_data["image_url"])
            if image is None:
                continue

            result = run_detection(image)
            if result["status"] != "nothing detected":
                # Extract first detection info
                first_detection = result["detections"][0] if result["detections"] else {}
                detected_class = first_detection.get("class", "unknown")
                confidence = first_detection.get("confidence", 0.0)

                # Avoid duplicate alerts
                existing = db.collection("alerts").where("image_location", "==", image_data["image_url"]).get()
                if not existing:
                    # Get forest name
                    forest_doc = db.collection("forestLocations").document(location_id).get()
                    forest_name = forest_doc.get("forest_name") if forest_doc.exists else "Unknown"

                    # Create alert
                    alert_ref = db.collection("alerts").document()
                    alert_ref.set({
                        "forest_name": forest_name,
                        "forest_location_id": location_id,
                        "image_location": image_data["image_url"],
                        "detection_status": "active",
                        "timestamp": datetime.utcnow(),
                        "alert_id": alert_ref.id
                    })

                    # Update image alert status
                    db.collection("forestLocations") \
                        .document(location_id) \
                        .collection("drones") \
                        .document(image_data["drone_id"]) \
                        .collection("images") \
                        .document(image_data["image_doc_id"]) \
                        .update({"alert_status": "active"})

                    # Store fire event for frontend
                    with simulation_lock:
                        simulation_state["fire_events"].append({
                            "coords": {
                                "latitude": image_data["latitude"],
                                "longitude": image_data["longitude"]
                            },
                            "image_url": image_data["image_url"],
                            "forest_name": forest_name,
                            "class": detected_class,
                            "confidence": confidence,
                            "location_id": location_id 
                        })
                        # Keep only the most recent 4
                        simulation_state["fire_events"] = simulation_state["fire_events"][-MAX_DETECTIONS:]

                    total_detected += 1
                    print(f"🔥 Alert created at {forest_name} ({image_data['latitude']}, {image_data['longitude']})")

                await asyncio.sleep(DETECTION_DELAY)
    except Exception as e:
        print(f"❌ Simulation error: {e}")
    finally:
        with simulation_lock:
            simulation_state["running"] = False
            simulation_state["thread"] = None

def start_simulation():
    with simulation_lock:
        if simulation_state["running"]:
            print("⚠️ Simulation already running — skipping")
            return

        print("🚀 Starting fire simulation thread...")
        simulation_state["running"] = True

        def run_simulation():
            try:
                # Create new event loop for the thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(simulate_fire_detection())
            except Exception as e:
                print(f"❌ Thread error: {e}")
            finally:
                with simulation_lock:
                    simulation_state["running"] = False
                    simulation_state["thread"] = None

        # Start the thread and store reference
        thread = threading.Thread(target=run_simulation, daemon=True)
        simulation_state["thread"] = thread
        thread.start()

def stop_simulation():
    with simulation_lock:
        if simulation_state["running"]:
            print("🛑 Stopping simulation")
            simulation_state["running"] = False
            if simulation_state["thread"] and simulation_state["thread"].is_alive():
                simulation_state["thread"].join(timeout=1.0)
        else:
            print("ℹ️ Simulation not running - nothing to stop")