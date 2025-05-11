import random
import cv2
import numpy as np
import os
import urllib.parse
import pathlib
from .config import db, bucket

def get_random_image_from_location(location_id):
    """Get a random image from a specific forest location (in memory only)."""
    drones_ref = db.collection("forestLocations").document(str(location_id)).collection("drones")
    drones = [doc.id for doc in drones_ref.stream()]

    if not drones:
        return None

    selected_drone = random.choice(drones)

    images_ref = drones_ref.document(selected_drone).collection("images")
    images = [doc.to_dict() for doc in images_ref.stream()]

    if not images:
        return None

    selected_image = random.choice(images)

    try:
        encoded_path = selected_image['image_url'].split('/o/')[1].split('?')[0]
        decoded_path = urllib.parse.unquote(encoded_path)
        blob = bucket.blob(decoded_path)

        # Download and decode image in memory
        image_data = blob.download_as_bytes()
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode the image.")

        print(f"Image loaded from Firebase, shape: {image.shape}")

        return {
            'image': image,
            'location_id': location_id,
            'drone_id': selected_drone,
            'original_data': selected_image
        }

    except Exception as e:
        print(f"Error downloading or processing image: {str(e)}")
        return None
