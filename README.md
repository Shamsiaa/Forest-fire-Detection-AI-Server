# Forest-fire-Detection-and-Prevenetion-using-AI
🚀 Overview
This project is a comprehensive forest fire detection and prevention system that integrates:

🛰️ AI-based image detection of fire and smoke using drone images (YOLOv8, Faster R-CNN).

🌡️ Arduino-based sensor network to monitor environmental conditions such as temperature, humidity, CO level, flame presence, and soil moisture.

📡 Wireless communication using NRF24L01 for sensor data transmission.

☁️ Cloud backend (FastAPI + Firebase) for real-time data aggregation and alerting.

📱 React Native mobile app for live monitoring, map-based alerts, region-specific details, and emergency calls.

🎯 Project Goals
Early detection of forest fires using both sensor anomalies and AI-based visual analysis.

Deliver real-time alerts with geolocation to forest authorities.

Provide a low-cost, modular, and scalable solution for fire-prone areas in Turkey and beyond.

🛠️ Architecture
🔧 Hardware
Sensor Node (Arduino):

Temperature and Humidity Sensor

Flame Sensor

Soil Moisture Sensor

Gas Sensor (CO)

GPS Module

NRF24L01 Module

Gateway Node (NodeMCU):

NRF24L01 (receiver)

Wi-Fi communication with FastAPI backend

💻 Software
AI Models: YOLOv8, Faster R-CNN (trained on wildfire dataset)

Backend: FastAPI with endpoints for simulation, alerts, and map data

Database: Firebase (Firestore & Storage)

Frontend: React Native (Expo), Stack Navigation
