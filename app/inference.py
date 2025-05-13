from ultralytics import YOLO
import numpy as np
from typing import Dict, Any, List

# Load the model once
model = YOLO("model/best.pt")

def run_detection(image: np.ndarray) -> Dict[str, Any]:
    """Run detection on an image array using YOLO and return parsed results."""
    if image is None or not isinstance(image, np.ndarray):
        raise ValueError("❌ Invalid image provided for detection.")

    print("🔍 Running YOLO detection...")
    
    # Run YOLO prediction (you can consider resizing or altering conf thresholds for better performance)
    results = model.predict(image, conf=0.6)
    
    detections: List[Dict[str, Any]] = []
    status = "nothing detected"

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = round(float(box.conf[0]), 2)
            bbox = list(map(float, box.xyxy[0].tolist()))
            class_name = model.names[cls_id]

            # Only include detections for "fire" or "smoke"
            if class_name.lower() in ["fire", "smoke"]:
                detections.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": bbox
                })
                status = f"{class_name} detected"

    print(f"✅ Detection complete. Status: {status}, Total detections: {len(detections)}")

    # If no detections for fire/smoke, ensure we return a status of "nothing detected"
    if len(detections) == 0:
        status = "nothing detected"

    return {
        "status": status,
        "detections": detections
    }
