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
    results = model.predict(image, conf=0.6)
    
    detections: List[Dict[str, Any]] = []
    status = "nothing detected"

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = round(float(box.conf[0]), 2)
            bbox = list(map(float, box.xyxy[0].tolist()))
            class_name = model.names[cls_id]

            detections.append({
                "class": class_name,
                "confidence": conf,
                "bbox": bbox
            })

            if class_name.lower() in ["fire", "smoke"]:
                status = f"{class_name} detected"

    print(f"✅ Detection complete. Status: {status}, Total detections: {len(detections)}")

    return {
        "status": status,
        "detections": detections
    }
