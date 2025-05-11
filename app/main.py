import random
import cv2
import os
import time
import gc
from firebase.db_operations import get_random_image_from_location
from .inference import run_detection  # This should accept a NumPy image, not a file path

def save_results(image, detections, location_id):
    """Draw detections and save image to disk."""
    for detection in detections:
        x1, y1, x2, y2 = map(int, detection['bbox'])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{detection['class']} {detection['confidence']:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Optionally add location info
    cv2.putText(image, f"Location: {location_id}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"location_{location_id}_output.jpg")
    cv2.imwrite(output_path, image)
    print(f"Saved annotated image for Location {location_id} to {output_path}")

def test_firebase_image_access_and_inference(location_id=1):
    try:
        # Step 1: Get a random image from Firebase (in memory)
        image_data = get_random_image_from_location(location_id)
        if not image_data:
            print(f"No images found for location {location_id}")
            return

        image = image_data['image']
        print(f"Image fetched from Firebase for Location {location_id}, shape: {image.shape}")

        # Step 2: Run inference (on the image, not a path)
        results = run_detection(image)

        # Step 3: Handle results
        if results['detections']:
            print(f"Inference results for Location {location_id}:")
            for detection in results['detections']:
                print(f"- {detection['class']} (confidence: {detection['confidence']:.2f})")

            save_results(results['image'], results['detections'], location_id)
        else:
            print(f"Inference failed or no fire/smoke detected for Location {location_id}.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        time.sleep(1)
        gc.collect()

if __name__ == "__main__":
    test_firebase_image_access_and_inference(location_id=1)
