from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from firebase.config import db
from datetime import datetime

router = APIRouter()

class AlertUpdate(BaseModel):
    status: str

@router.get("/")
async def get_alerts():
    """Get all alerts, sorted by most recent first"""
    try:
        alerts_ref = db.collection("alerts")
        docs = alerts_ref.order_by("timestamp", direction="DESCENDING").stream()
        
        alerts = []
        for doc in docs:
            alert_data = doc.to_dict()
            alert_data["alert_id"] = doc.id
            alerts.append(alert_data)
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{alert_id}")
async def update_alert_status(
    alert_id: str,
    update_data: AlertUpdate = Body(...)
):
    """Update alert status (active, help_requested, dismissed)"""
    valid_statuses = ["active", "help_requested", "dismissed"]
    if update_data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of {valid_statuses}"
        )

    try:
        alert_ref = db.collection("alerts").document(alert_id)
        alert_doc = alert_ref.get()
        
        if not alert_doc.exists:
            raise HTTPException(status_code=404, detail="Alert not found")

        # Update alert status
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
        raise HTTPException(
            status_code=500,
            detail=f"Error updating alert: {str(e)}"
        )