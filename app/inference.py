from ultralytics import YOLO
import cv2
from typing import Dict, Any
import os
# Load the model
model = YOLO("model/best.pt")

def run_detection(image_path: str) -> Dict[str, Any]:
    """Run detection on an image file and return results"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")

    # Run inference
    results = model.predict(img, conf=0.6)
    detections = []
    status = "nothing detected"
    
    # Annotate image with bounding boxes and labels
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            class_name = model.names[cls]
            
            # Draw bounding box on the image
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green color box
            label = f"{class_name} {conf:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            detections.append({
                "class": class_name,
                "confidence": conf,
                "bbox": bbox
            })
            
            # Update status if fire or smoke is detected
            if class_name.lower() in ["fire", "smoke"]:
                status = f"{class_name} detected"
    
    # Save the result image with annotations
   # output_dir = "output_results"
   # os.makedirs(output_dir, exist_ok=True)
    #output_image_path = os.path.join(output_dir, "detected_image.jpg")
    #cv2.imwrite(output_image_path, img)
    #print(f"Results saved to {output_image_path}")

    return {
        "status": status,
        "detections": detections,
        "image": img  # Return annotated image
    }
