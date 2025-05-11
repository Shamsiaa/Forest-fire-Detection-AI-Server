from ultralytics import YOLO
import cv2
from typing import Dict, Any
import numpy as np

# Load the model once at import
model = YOLO("model/best.pt")

def run_detection(image: np.ndarray) -> Dict[str, Any]:
    """Run detection on an in-memory image and return results."""
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("Invalid image provided for detection")

    # Run inference directly on the image
    results = model.predict(image, conf=0.6)
    detections = []
    status = "nothing detected"

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            class_name = model.names[cls]

            detections.append({
                "class": class_name,
                "confidence": conf,
                "bbox": bbox
            })

            if class_name.lower() in ["fire", "smoke"]:
                status = f"{class_name} detected"

    return {
        "status": status,
        "detections": detections,
        "image": image  # Return the original image for optional drawing
    }
