import random
import cv2
import numpy as np
import urllib.parse
from .config import db, bucket
import numpy as np


def get_random_image_from_location(location_id):
    """Get a random image with coordinates from a forest location (in memory only)."""
    try:
        # Step 1: Fetch drones for the location
        drones_ref = db.collection("forestLocations").document(str(location_id)).collection("drones")
        drones = [doc.id for doc in drones_ref.stream()]
        if not drones:
            print(f"No drones found for location {location_id}")
            return None

        # Step 2: Select a random drone and fetch its images
        selected_drone = random.choice(drones)
        images_ref = drones_ref.document(selected_drone).collection("images")
        images = [doc.to_dict() for doc in images_ref.stream()]
        if not images:
            print(f"No images found for drone {selected_drone} at location {location_id}")
            return None

        # Step 3: Select a random image
        selected_image = random.choice(images)

        # Validate fields
        if 'image_url' not in selected_image or 'coords' not in selected_image:
            print("Missing image_url or coords in selected image.")
            return None

        coords = selected_image['coords']
        latitude = coords.get('latitude')
        longitude = coords.get('longitude')

        if latitude is None or longitude is None:
            print("Invalid coordinates in image metadata.")
            return None

        # Step 4: Download and decode the image
        encoded_path = selected_image['image_url'].split('/o/')[1].split('?')[0]
        decoded_path = urllib.parse.unquote(encoded_path)
        blob = bucket.blob(decoded_path)

        image_data = blob.download_as_bytes()
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image.")

        print(f"Image loaded successfully for location {location_id}, drone {selected_drone}")

        return {
            'image': image,
            'location_id': location_id,
            'drone_id': selected_drone,
            'latitude': latitude,
            'longitude': longitude,
            'original_data': selected_image  # optional, can be removed
        }

    except Exception as e:
        print(f"Error downloading or processing image: {str(e)}")
        return None
