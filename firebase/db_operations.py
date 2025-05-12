import random
import cv2
import numpy as np
import urllib.parse
from .config import db, bucket

# Store missing field logs
missing_fields_log = []

def get_random_image_from_location(location_id):
    """Get a random valid image (with coordinates and URL) from a forest location."""
    try:
        # Fetch the single drone ID under this location
        drones_ref = db.collection("forestLocations").document(str(location_id)).collection("drones")
        drones = [doc.id for doc in drones_ref.stream()]
        if not drones:
            print(f"No drones found for location {location_id}")
            return None

        selected_drone = drones[0]  # Only one drone per location
        images_ref = drones_ref.document(selected_drone).collection("images")

        # Filter only valid images
        images = []
        for doc in images_ref.stream():
            data = doc.to_dict()
            missing_fields = [k for k in ('image_url', 'latitude', 'longitude') if k not in data]

            if missing_fields:
                # Log the missing fields
                missing_fields_log.append({
                    'filename': data.get('filename', 'unknown'),
                    'missing_fields': missing_fields
                })
                print(f"⚠️ Skipping image due to missing fields: {', '.join(missing_fields)} in image {data.get('filename', 'unknown')}")
            else:
                images.append(data)

        if not images:
            print(f"No valid images found for drone {selected_drone} at location {location_id}")
            return None

        # Select a random valid image
        selected_image = random.choice(images)
        latitude = selected_image['latitude']
        longitude = selected_image['longitude']
        image_url = selected_image['image_url']

        # Log the image URL for debugging purposes
        if not image_url:
            print(f"❌ Image {selected_image.get('filename', 'unknown')} is missing image_url")

        # Download and decode the image
        encoded_path = image_url.split('/o/')[1].split('?')[0]
        decoded_path = urllib.parse.unquote(encoded_path)
        blob = bucket.blob(decoded_path)

        try:
            image_data = blob.download_as_bytes()
            image_np = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError(f"Failed to decode image: {selected_image.get('filename', 'unknown')}")
        except Exception as e:
            print(f"❌ Error decoding image {selected_image.get('filename', 'unknown')}: {str(e)}")
            return None

        print(f"✅ Image loaded: {selected_image.get('filename', 'Unnamed')} from location {location_id}")

        return {
            'image': image,
            'location_id': location_id,
            'drone_id': selected_drone,
            'latitude': latitude,
            'longitude': longitude,
            'original_data': selected_image
        }

    except Exception as e:
        print(f"❌ Error downloading or processing image: {str(e)}")
        return None
