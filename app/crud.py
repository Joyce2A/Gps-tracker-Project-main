# ## File: app/crud.py
# from app.database import db
# from bson import ObjectId
# from typing import Optional
# from datetime import datetime


# async def create_user(email: str, password_hash: str, role: str):
#     doc = {"email": email, "password_hash": password_hash, "role": role, "created_at": datetime.utcnow()}
#     res = await db["users"].insert_one(doc)
#     return str(res.inserted_id)




# async def create_device(doc: dict):
#     res = await db["devices"].insert_one(doc)
#     return str(res.inserted_id)




# async def get_device_by_device_id(device_id: str) -> Optional[dict]:
#     return await db["devices"].find_one({"device_id": device_id})




# async def update_device_last_seen(device_id: str, timestamp: datetime):
#     await db["devices"].update_one({"device_id": device_id}, {"$set": {"last_seen": timestamp}})


# # in app/crud.py
# async def get_latest_location_by_device(device_id: str):
#     return await db["device_locations"].find_one(
#         {"device_id": device_id}, sort=[("timestamp", -1)]
#     )

# async def get_location_history_by_device(device_id: str, limit: int = 50):
#     cursor = db["device_locations"].find({"device_id": device_id}).sort("timestamp", -1).limit(limit)
#     return await cursor.to_list(length=limit)



# async def insert_location(doc: dict):
#     await db["locations"].insert_one(doc)




# async def insert_alert(doc: dict):
#     await db["alerts"].insert_one(doc)




# async def list_devices():
#     cursor = db["devices"].find({})
#     out = []
#     async for d in cursor:
#         d["id"] = str(d.get("_id"))
#         out.append(d)
#     return out



# async def list_devices_by_user_id(user_id: str):
#     return await db.devices.find({"user_id": user_id}).to_list(length=100)




# async def get_last_location(device_id: str):
#     return await db["locations"].find_one({"device_id": device_id}, sort=[("timestamp", -1)])


# async def list_alerts(limit: int = 100):
#     cursor = db["alerts"].find({}).sort("timestamp", -1).limit(limit)
#     out = []
#     async for a in cursor:
#         a["id"] = str(a.get("_id"))
#         out.append(a)
#     return out


from app.database import db
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timedelta
import logging

# Configure module logger
logger = logging.getLogger(__name__)


# USER OPERATIONS

async def create_user(email: str, password_hash: str, role: str = "user") -> str:
    """Create a new user"""
    doc = {
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "email_verified": False
    }
    res = await db["users"].insert_one(doc)
    return str(res.inserted_id)


async def find_user_by_email(email: str) -> Optional[dict]:
    """Find user by email address"""
    user = await db["users"].find_one({"email": email})
    if user and "_id" in user:
        user["id"] = str(user["_id"])
    return user


async def find_user_by_id(user_id: str) -> Optional[dict]:
    """Find user by MongoDB _id"""
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if user and "_id" in user:
            user["id"] = str(user["_id"])
        return user
    except:
        return None


async def update_user_password(user_id: str, hashed_password: str) -> bool:
    """Update user's password"""
    try:
        result = await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": hashed_password, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except:
        return False


async def store_password_reset_token(token: str, user_id: str, expires_at: datetime) -> bool:
    """Store password reset token in database"""
    try:
        # Clean up expired tokens first
        await db["password_reset_tokens"].delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        # Convert user_id string to ObjectId if needed
        from bson import ObjectId
        try:
            user_obj_id = ObjectId(user_id)
        except:
            # If user_id is already ObjectId
            user_obj_id = user_id
        
        # Store the token
        token_doc = {
            "token": token,
            "user_id": user_obj_id,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.utcnow()
        }
        
        result = await db["password_reset_tokens"].insert_one(token_doc)
        
        logger.info(f" Password reset token stored for user: {user_id}")
        logger.debug(f"Token ID: {result.inserted_id}")
        
        return True
        
    except Exception as e:
        logger.error(f" Failed to store password reset token: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def get_password_reset_token(token: str) -> Optional[dict]:
    """Retrieve password reset token"""
    token_data = await db["password_reset_tokens"].find_one({
        "token": token,
        "used": False,
        "expires_at": {"$gt": datetime.utcnow()}  # Not expired
    })
    
    if token_data and "_id" in token_data:
        token_data["id"] = str(token_data["_id"])
        token_data["user_id"] = str(token_data["user_id"])
    
    return token_data


async def mark_password_reset_token_used(token: str) -> bool:
    """Mark a password reset token as used"""
    try:
        result = await db["password_reset_tokens"].update_one(
            {"token": token},
            {"$set": {"used": True, "used_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except:
        return False


async def cleanup_expired_tokens() -> int:
    """Clean up expired password reset tokens"""
    result = await db["password_reset_tokens"].delete_many({
        "expires_at": {"$lt": datetime.utcnow()}
    })
    return result.deleted_count


#  DEVICE OPERATIONS 

async def create_device(doc: dict) -> str:
    """Create a new device"""
    doc["created_at"] = datetime.utcnow()
    res = await db["devices"].insert_one(doc)
    return str(res.inserted_id)


async def get_device_by_device_id(device_id: str) -> Optional[dict]:
    """Get device by device_id"""
    device = await db["devices"].find_one({"device_id": device_id})
    if device and "_id" in device:
        device["id"] = str(device["_id"])
    return device


async def update_device_last_seen(device_id: str, timestamp: datetime):
    """Update device's last seen timestamp"""
    await db["devices"].update_one(
        {"device_id": device_id},
        {"$set": {"last_seen": timestamp, "updated_at": datetime.utcnow()}}
    )


async def list_devices() -> List[dict]:
    """List all devices"""
    cursor = db["devices"].find({})
    out = []
    async for d in cursor:
        d["id"] = str(d.get("_id"))
        out.append(d)
    return out


async def list_devices_by_user_id(user_id: str) -> List[dict]:
    """List devices by user ID"""
    cursor = db["devices"].find({"user_id": user_id})
    devices = await cursor.to_list(length=100)
    
    for device in devices:
        if "_id" in device:
            device["id"] = str(device["_id"])
    
    return devices


# LOCATION OPERATIONS 

async def get_latest_location_by_device(device_id: str) -> Optional[dict]:
    """Get latest location for a device"""
    location = await db["device_locations"].find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )
    if location and "_id" in location:
        location["id"] = str(location["_id"])
    return location


async def get_location_history_by_device(device_id: str, limit: int = 50) -> List[dict]:
    """Get location history for a device"""
    cursor = db["device_locations"].find({"device_id": device_id}).sort("timestamp", -1).limit(limit)
    locations = await cursor.to_list(length=limit)
    
    for location in locations:
        if "_id" in location:
            location["id"] = str(location["_id"])
    
    return locations


async def insert_location(doc: dict):
    """Insert a new location record"""
    doc["created_at"] = datetime.utcnow()
    await db["locations"].insert_one(doc)


async def get_last_location(device_id: str) -> Optional[dict]:
    """Get last known location for a device"""
    location = await db["locations"].find_one(
        {"device_id": device_id},
        sort=[("timestamp", -1)]
    )
    if location and "_id" in location:
        location["id"] = str(location["_id"])
    return location


#  ALERT OPERATIONS 

async def insert_alert(doc: dict):
    """Insert a new alert"""
    doc["created_at"] = datetime.utcnow()
    await db["alerts"].insert_one(doc)


async def list_alerts(limit: int = 100) -> List[dict]:
    """List all alerts"""
    cursor = db["alerts"].find({}).sort("timestamp", -1).limit(limit)
    out = []
    async for a in cursor:
        a["id"] = str(a.get("_id"))
        out.append(a)
    return out


async def get_alerts_by_device(device_id: str, limit: int = 50) -> List[dict]:
    """Get alerts for a specific device"""
    cursor = db["alerts"].find({"device_id": device_id}).sort("timestamp", -1).limit(limit)
    alerts = await cursor.to_list(length=limit)
    
    for alert in alerts:
        if "_id" in alert:
            alert["id"] = str(alert["_id"])
    
    return alerts