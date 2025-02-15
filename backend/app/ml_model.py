import cv2
import torch
import numpy as np
from ultralytics import YOLO
import os
import datetime

# Load YOLOv8 model
MODEL_PATH = "ml_model/model_weights/best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"YOLOv8 model weights not found at {MODEL_PATH}")

model = YOLO(MODEL_PATH)

# Define storage conditions for different categories
STORAGE_CONDITIONS = {
    "Tablet": {"temp_range": (15, 25), "humidity_range": (30, 50)},  
    "Liquid": {"temp_range": (2, 8), "humidity_range": (20, 40)},   # Refrigerator
    "Misc": {"temp_range": (10, 30), "humidity_range": (20, 60)}
}

def preprocess_image(image_path):
    """
    Loads and preprocesses an image before YOLO detection.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Error loading image: {image_path}")

    return image

def check_expiry(expiry_date):
    """
    Checks if the medicine is expired.
    :param expiry_date: String (YYYY-MM-DD)
    :return: Boolean (True if expired)
    """
    today = datetime.date.today()
    try:
        expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        return expiry < today  # True if expired
    except ValueError:
        return None  # Invalid date format

def detect_objects(image_path, storage_temp=None, storage_humidity=None):
    """
    Runs YOLOv8 object detection and filters medicines based on:
    - Expiry date
    - Storage conditions (temperature, humidity)
    """
    image = preprocess_image(image_path)
    results = model(image)
    detected_items = []

    for result in results:
        for i, box in enumerate(result.boxes.xyxy):
            x1, y1, x2, y2 = map(int, box)
            confidence = float(result.boxes.conf[i])  
            class_id = int(result.boxes.cls[i])  # YOLO class ID
            label = model.names[class_id]  # Medicine name from YOLO

            # Simulating metadata retrieval (expiry & storage needs)
            expiry_date = "2025-12-01"  # Normally fetched from DB
            category = "Tablet" if "tablet" in label.lower() else "Liquid" if "syrup" in label.lower() else "Misc"
            
            # Check expiry
            expired = check_expiry(expiry_date)

            # Check storage conditions
            storage_ok = True
            if storage_temp and storage_humidity:
                ideal_conditions = STORAGE_CONDITIONS.get(category, {})
                temp_range = ideal_conditions.get("temp_range", (0, 50))
                humidity_range = ideal_conditions.get("humidity_range", (0, 100))

                if not (temp_range[0] <= storage_temp <= temp_range[1]) or not (humidity_range[0] <= storage_humidity <= humidity_range[1]):
                    storage_ok = False

            detected_items.append({
                "name": label,
                "category": category,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "confidence": round(confidence, 2),
                "expiry_date": expiry_date,
                "expired": expired,
                "storage_ok": storage_ok,
                "storage_temp": storage_temp,
                "storage_humidity": storage_humidity
            })
    
    return detected_items
