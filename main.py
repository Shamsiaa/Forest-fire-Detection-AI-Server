# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ultralytics import YOLO
import shutil
import cv2
import os
import uuid
import io
from typing import Dict, Any

app = FastAPI()

# Load YOLO model
model = YOLO("model/best.pt")

@app.get("/")
async def root():
    return {
        "message": "YOLOv8 Object Detection API",
        "endpoints": {
            "docs": "/docs",
            "inference": "POST /inference/"
        }
    }

@app.post("/inference/")
async def run_inference(file: UploadFile = File(...), return_json: bool = False):
    temp_file_path = f"temp_{uuid.uuid4()}.jpg"
    detection_status = "nothing detected"
    detected_objects = []
    
    try:
        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read image
        img = cv2.imread(temp_file_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Run YOLOv8 inference
        results = model.predict(img, conf=0.2)
        
        # Process detections
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
                class_name = model.names[cls]
                
                detected_objects.append({
                    "class": class_name,
                    "confidence": conf,
                    "bbox": bbox
                })
                
                # Update detection status if fire or smoke is found
                if class_name.lower() in ["fire", "smoke"]:
                    detection_status = f"{class_name} detected"
                
                # Draw bounding boxes
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} {conf:.2f}"
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # If user wants JSON response instead of image
        if return_json:
            return JSONResponse(content={
                "status": detection_status,
                "detections": detected_objects
            })
        
        # Add detection status text to image
        cv2.putText(img, detection_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Encode image to JPEG
        _, img_encoded = cv2.imencode(".jpg", img)
        return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)