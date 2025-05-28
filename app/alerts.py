from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel
from firebase.config import db
from datetime import datetime
from twilio.rest import Client
import os
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class AlertUpdate(BaseModel):
    status: str

class SMSRequest(BaseModel):
    alert_id: str
    station_name: str
    forest_name: str

# Initialize Twilio client
try:
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    your_phone = os.getenv('PHONE_NUMBER')

    if not all([account_sid, auth_token, twilio_phone, your_phone]):
        logger.warning("Missing one or more Twilio environment variables")

    client = Client(account_sid, auth_token)
    logger.info("Twilio client initialized")
except Exception as e:
    logger.error(f"Twilio initialization failed: {e}", exc_info=True)
    client = None

async def get_fire_stations(location_id, station_id: Optional[str] = None):
    try:
        stations_ref = db.collection("forestLocations").document(location_id).collection("firestations")

        if station_id:
            doc = stations_ref.document(station_id).get()
            if not doc.exists:
                return []
            data = doc.to_dict()
            return [{
                "id": station_id,
                "name": data.get("station_name", f"Station {station_id}"),
                "phone": data.get("phone", "")
            }]
        else:
            return [{
                "id": doc.id,
                "name": doc.to_dict().get("station_name", f"Station {doc.id}"),
                "phone": doc.to_dict().get("phone", "")
            } for doc in stations_ref.stream()]
    except Exception as e:
        logger.error(f"Error fetching stations: {e}", exc_info=True)
        return []

@router.get("/")
async def get_alerts(
    forest_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None)
):
    try:
        alerts_ref = db.collection("alerts").where("detection_status", "==", "active")
        if forest_id:
            alerts_ref = alerts_ref.where("forest_location_id", "==", forest_id)

        alerts = []
        for doc in alerts_ref.stream():
            data = doc.to_dict()
            data["alert_id"] = doc.id
            data["fire_stations"] = await get_fire_stations(data["forest_location_id"], station_id)

            if not station_id or data["fire_stations"]:
                alerts.append(data)

        alerts.sort(key=lambda x: x.get("timestamp"), reverse=True)
        return alerts
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@router.patch("/{alert_id}")
async def update_alert_status(alert_id: str, update_data: AlertUpdate):
    try:
        if update_data.status not in ["active", "help_requested", "dismissed"]:
            raise HTTPException(status_code=400, detail="Invalid status")

        alert_ref = db.collection("alerts").document(alert_id)
        if not alert_ref.get().exists:
            raise HTTPException(status_code=404, detail="Alert not found")

        alert_ref.update({
            "detection_status": update_data.status,
            "updated_at": datetime.utcnow()
        })
        return {
            "status": "success",
            "alert_id": alert_id,
            "new_status": update_data.status
        }
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Update failed")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    try:
        alert_ref = db.collection("alerts").document(alert_id)
        if not alert_ref.get().exists:
            raise HTTPException(status_code=404, detail="Alert not found")

        alert_ref.delete()
        return {
            "status": "success",
            "alert_id": alert_id,
            "message": "Alert deleted"
        }
    except Exception as e:
        logger.error(f"Delete failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Delete failed")

@router.post("/send-alert-sms")
async def send_alert_sms(request: SMSRequest):
    try:
        if not client:
            raise Exception("Twilio client not configured")
        
        message = client.messages.create(
            body=f"🚨 FIRE ALERT! Assistance requested at {request.station_name} in {request.forest_name} (Alert ID: {request.alert_id})",
            from_=twilio_phone,
            to=your_phone
        )
        return {
            "status": "success",
            "message_sid": message.sid,
            "alert_id": request.alert_id
        }
    except Exception as e:
        logger.error(f"SMS send failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send SMS")
