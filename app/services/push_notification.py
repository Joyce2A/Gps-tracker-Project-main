# app/services/push_notification.py
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-service-account.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

async def send_alert_notification(
    user_id: str,
    alert_type: str,
    message: str,
    asset_id: str = None
):
    """Send push notification when alert is triggered"""
    
    titles = {
        "geofence_breach": "⚠️ Geofence Breach",
        "low_battery":     "🔋 Low Battery Alert",
        "sos":             "🆘 SOS Alert!",
        "device_offline":  "📡 Device Offline",
        "speed_violation": "🚨 Speed Violation",
    }
    
    notification = messaging.Notification(
        title=titles.get(alert_type, "GPS Alert"),
        body=message,
    )
    
    msg = messaging.Message(
        notification=notification,
        topic=f"user_{user_id}",   # sends to user's device
        data={
            "alert_type": alert_type,
            "asset_id":   asset_id or "",
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
        },
    )
    
    try:
        response = messaging.send(msg)
        print(f"Push notification sent: {response}")
    except Exception as e:
        print(f"Push notification failed: {e}")
        
        