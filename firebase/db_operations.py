import random
import cv2
import numpy as np
import os
import urllib.parse
import pathlib
from .config import db, bucket

def get_random_image_from_location(location_id):
    """Get a random image from a specific forest location."""
    drones_ref = db.collection("forestLocations").document(str(location_id)).collection("drones")
    drones = [doc.id for doc in drones_ref.stream()]

    if not drones:
        return None

    # Select random drone
    selected_drone = random.choice(drones)

    # Get all images for this drone
    images_ref = drones_ref.document(selected_drone).collection("images")
    images = [doc.to_dict() for doc in images_ref.stream()]

    if not images:
        return None

    # Select random image
    selected_image = random.choice(images)

    try:
        # Decode the image path from Firebase Storage URL
        encoded_path = selected_image['image_url'].split('/o/')[1].split('?')[0]
        decoded_path = urllib.parse.unquote(encoded_path)
        blob = bucket.blob(decoded_path)

        # Read the image directly from Firebase Storage
        image_data = blob.download_as_bytes()
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode the image.")

        print(f"Image loaded from Firebase, shape: {image.shape}")

        # Run inference on the image (use your own inference function here)
        detections = run_inference(image)  # Assuming it returns detections and confidence scores
        
        # Save results with bounding boxes and confidence scores
        output_path = save_results_with_bboxes(image, detections, location_id)

        return {
            'image_path': output_path,
            'location_id': location_id,
            'drone_id': selected_drone,
            'original_data': selected_image
        }

    except Exception as e:
        print(f"Error downloading or processing image: {str(e)}")
        return None


def save_results_with_bboxes(image, detections, location_id):
    """Save the image with bounding boxes and confidence scores drawn on it."""
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection['bbox'])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{detection['class']} {detection['confidence']:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save the image with annotations
    output_dir = "output_results"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"location_{location_id}.jpg")
    cv2.imwrite(output_path, image)
    print(f"Results saved to {output_path}")
    return output_path


def run_inference(image):
    """Perform inference on the image and return detections (this is a placeholder)."""
    # Replace with actual inference logic
    # Example of detection results: [{'bbox': [100, 100, 200, 200], 'class': 'fire', 'confidence': 0.85}]
    return [{'bbox': [100, 100, 200, 200], 'class': 'fire', 'confidence': 0.85}]


if __name__ == "__main__":
    location_id = 1
    result = get_random_image_from_location(location_id)
    if result:
        print(f"Inference results saved at: {result['image_path']}")