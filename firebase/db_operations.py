import random
import cv2
import numpy as np
import urllib.parse
from .config import db, bucket

missing_fields_log = []

def get_valid_images_from_location(location_id):
    """Retrieve all valid images with necessary fields from a forest location."""
    try:
        drones_ref = db.collection("forestLocations").document(str(location_id)).collection("drones")
        drones = [doc.id for doc in drones_ref.stream()]
        if not drones:
            print(f"No drones found for location {location_id}")
            return []

        selected_drone = drones[0]
        images_ref = drones_ref.document(selected_drone).collection("images")

        valid_images = []
        for doc in images_ref.stream():
            data = doc.to_dict()
            missing_fields = [k for k in ('image_url', 'latitude', 'longitude') if k not in data]
            if missing_fields:
                missing_fields_log.append({
                    'filename': data.get('filename', 'unknown'),
                    'missing_fields': missing_fields
                })
                print(f"⚠️ Skipping image due to missing fields: {', '.join(missing_fields)} in image {data.get('filename', 'unknown')}")
            else:
                valid_images.append({
                    'image_url': data['image_url'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'original_data': data,
                    'drone_id': selected_drone,
                    'image_doc_id': doc.id  # 🔥 Add this
                })


        return valid_images

    except Exception as e:
        print(f"❌ Error retrieving images from location {location_id}: {str(e)}")
        return []

def load_image_from_url(image_url):
    """Download and decode image from Firebase Storage using its URL."""
    try:
        encoded_path = image_url.split('/o/')[1].split('?')[0]
        decoded_path = urllib.parse.unquote(encoded_path)
        blob = bucket.blob(decoded_path)

        image_data = blob.download_as_bytes()
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image.")

        return image

    except Exception as e:
        print(f"❌ Error downloading or decoding image from URL: {str(e)}")
        return None
