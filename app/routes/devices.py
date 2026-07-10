# ## File: app/routers/devices.py

# from fastapi import APIRouter, Depends, HTTPException
# from app.schemas import DeviceCreate, DeviceOut, DeviceUpdate
# from app.auth import require_role, get_current_user
# from app.database import db
# from datetime import datetime
# from typing import List

# router = APIRouter()

# from datetime import datetime, timedelta

# OFFLINE_THRESHOLD = timedelta(minutes=2)

# def calculate_status(last_seen):
#     if not last_seen:
#         return "offline"
#     if datetime.utcnow() - last_seen <= OFFLINE_THRESHOLD:
#         return "online"
#     return "offline"


# @router.post("/", response_model=DeviceOut)
# async def add_device(device: DeviceCreate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Check for duplicate device_id
#         existing_device = await db["devices"].find_one({"device_id": device.device_id})
#         if existing_device:
#             raise HTTPException(status_code=400, detail="Device ID already exists")
        
#         # Validate battery level
#         if device.battery_level is not None and not (0 <= device.battery_level <= 100):
#             raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")
        
#         # Validate device_status if provided
#         valid_statuses = ["online", "offline", "maintenance", "error"]
#         if device.device_status and device.device_status not in valid_statuses:
#             raise HTTPException(status_code=400, detail=f"Device status must be one of: {', '.join(valid_statuses)}")
        
#         user_id = str(current_user["_id"])
#         current_time = datetime.utcnow().isoformat() 

#         device_data = {
#             "user_id": user_id,
#             "device_id": device.device_id,
#             "device_name": device.device_name,
#             "device_model": device.device_model,
#             "battery_level": device.battery_level,
#             "device_status": device.device_status or "offline",  # Default status
#             "time_stamp": current_time
#         }

#         result = await db["devices"].insert_one(device_data)

#         # Return the created device with the generated ID
#         return DeviceOut(
#             id=str(result.inserted_id),
#             **device.dict(),
#             time_stamp=current_time
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create device: {str(e)}")


# # Get all devices for the current logged-in user
# @router.get("/", response_model=List[DeviceOut])
# async def get_devices(current_user: dict = Depends(get_current_user)):
#     try:
#         user_id = str(current_user["_id"])
#         cursor = db["devices"].find({"user_id": user_id})
#         devices = await cursor.to_list(length=None)

#         if not devices:
#             return []  # Return empty list instead of 404 for better UX

#         return [
#             DeviceOut(
#                 id=str(d["_id"]),
#                 device_id=d["device_id"],
#                 device_name=d.get("device_name"),
#                 device_model=d.get("device_model"),
#                 battery_level=d.get("battery_level"),
#                 device_status=d.get("device_status"),
#                 time_stamp=d.get("time_stamp")
#             )
#             for d in devices
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch devices: {str(e)}")


# # Get all devices for a specific user ID (admin only)
# @router.get("/by-user/{user_id}", response_model=List[DeviceOut])
# async def get_devices_by_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
#     try:
#         print(f"Searching for devices with user_id: {user_id}")
#         cursor = db["devices"].find({"user_id": user_id})
#         devices = await cursor.to_list(length=None)

#         if not devices:
#             return []  # Return empty list for consistency

#         return [
#             DeviceOut(
#                 id=str(d["_id"]),
#                 device_id=d["device_id"],
#                 device_name=d.get("device_name"),
#                 device_model=d.get("device_model"),
#                 battery_level=d.get("battery_level"),
#                 device_status=d.get("device_status"),
#                 time_stamp=d.get("time_stamp")
#             )
#             for d in devices
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch user devices: {str(e)}")


# # Get a specific device by device_id #only owner or admin
# @router.get("/by-device/{device_id}", response_model=DeviceOut)
# async def get_device_by_id(device_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         device = await db["devices"].find_one({"device_id": device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")

#         # Allow admin users to access any device
#         if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to access this device")

#         return DeviceOut(
#             id=str(device["_id"]),
#             device_id=device["device_id"],
#             device_name=device.get("device_name"),
#             device_model=device.get("device_model"),
#             battery_level=device.get("battery_level"),
#             # device_status=device.get("device_status"),
#             device_status=status,  # 👈 dynamic
#             time_stamp=device.get("time_stamp")
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch device: {str(e)}")


# # Update device details 
# @router.put("/by-device/{device_id}", response_model=DeviceOut)
# async def update_device(device_id: str, updates: DeviceUpdate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the device
#         device = await db["devices"].find_one({"device_id": device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")

#         # Ensure user owns the device or is admin
#         if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to update this device")

#         # Convert to dictionary and remove None values
#         update_data = {k: v for k, v in updates.dict(exclude_unset=True).items() if v is not None}
        
#         # Validate battery level if provided
#         if "battery_level" in update_data and not (0 <= update_data["battery_level"] <= 100):
#             raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")
        
#         # Validate device_status if provided
#         valid_statuses = ["online", "offline", "maintenance", "error"]
#         if "device_status" in update_data and update_data["device_status"] not in valid_statuses:
#             raise HTTPException(status_code=400, detail=f"Device status must be one of: {', '.join(valid_statuses)}")

#         if not update_data:
#             raise HTTPException(status_code=400, detail="No valid fields provided for update")

#         # Update timestamp to reflect modification time
#         update_data["time_stamp"] = datetime.utcnow().isoformat()

#         # Apply the update and return the updated document
#         result = await db["devices"].find_one_and_update(
#             {"device_id": device_id},
#             {"$set": update_data},
#             return_document=True  # Return the updated document
#         )

#         if not result:
#             raise HTTPException(status_code=404, detail="Device not found after update")

#         return DeviceOut(
#             id=str(result["_id"]),
#             device_id=result["device_id"],
#             device_name=result.get("device_name"),
#             device_model=result.get("device_model"),
#             battery_level=result.get("battery_level"),
#             device_status=result.get("device_status"),
#             time_stamp=result.get("time_stamp")
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update device: {str(e)}")


# @router.delete("/by-device/{device_id}")
# async def delete_device(device_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the device
#         device = await db["devices"].find_one({"device_id": device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")

#         # Ensure user owns the device or is admin
#         if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to delete this device")

#         # Delete the record
#         result = await db["devices"].delete_one({"device_id": device_id})

#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="Device not found or already deleted")

#         return {"message": f"Device '{device_id}' deleted successfully"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete device: {str(e)}")


# from fastapi import APIRouter, Depends, HTTPException
# from app.schemas import DeviceCreate, DeviceOut, DeviceUpdate
# from app.auth import require_role, get_current_user
# from app.database import db
# from datetime import datetime, timedelta
# from typing import List

# router = APIRouter()

# # --------------------------------------------------
# # ONLINE / OFFLINE CONFIG
# # --------------------------------------------------
# OFFLINE_THRESHOLD = timedelta(minutes=5)

# def calculate_status(last_seen: datetime | None) -> str:
#     if not last_seen:
#         return "offline"
#     if datetime.utcnow() - last_seen <= OFFLINE_THRESHOLD:
#         return "online"
#     return "offline"


# # --------------------------------------------------
# # CREATE DEVICE (MANUAL REGISTRATION)
# # --------------------------------------------------
# @router.post("/", response_model=DeviceOut)
# async def add_device(device: DeviceCreate, current_user: dict = Depends(get_current_user)):
#     existing_device = await db.devices.find_one({"device_id": device.device_id})
#     if existing_device:
#         raise HTTPException(status_code=400, detail="Device ID already exists")

#     if device.battery_level is not None and not (0 <= device.battery_level <= 100):
#         raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")

#     user_id = str(current_user["_id"])
#     now = datetime.utcnow()

#     device_data = {
#         "user_id": user_id,
#         "device_id": device.device_id,
#         "device_name": device.device_name,
#         "device_model": device.device_model,
#         "battery_level": device.battery_level,
#         "created_at": now,
#         "last_seen": None   # 👈 IMPORTANT (MQTT will update)
#     }

#     result = await db.devices.insert_one(device_data)

#     return DeviceOut(
#         id=str(result.inserted_id),
#         device_id=device.device_id,
#         device_name=device.device_name,
#         device_model=device.device_model,
#         battery_level=device.battery_level,
#         device_status="offline",
#         time_stamp=now
#     )


# # --------------------------------------------------
# # GET ALL DEVICES (LOGGED-IN USER)
# # --------------------------------------------------
# @router.get("/", response_model=List[DeviceOut])
# async def get_devices(current_user: dict = Depends(get_current_user)):
#     user_id = str(current_user["_id"])
#     devices = await db.devices.find({"user_id": user_id}).to_list(length=None)

#     response = []
#     for d in devices:
#         status = calculate_status(d.get("last_seen"))

#         response.append(DeviceOut(
#             id=str(d["_id"]),
#             device_id=d["device_id"],
#             device_name=d.get("device_name"),
#             device_model=d.get("device_model"),
#             battery_level=d.get("battery_level"),
#             device_status=status,           # ✅ dynamic
#             time_stamp=d.get("created_at")
#         ))

#     return response


# # --------------------------------------------------
# # GET DEVICES BY USER (ADMIN)
# # --------------------------------------------------
# @router.get("/by-user/{user_id}", response_model=List[DeviceOut])
# async def get_devices_by_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
#     devices = await db.devices.find({"user_id": user_id}).to_list(length=None)

#     response = []
#     for d in devices:
#         status = calculate_status(d.get("last_seen"))

#         response.append(DeviceOut(
#             id=str(d["_id"]),
#             device_id=d["device_id"],
#             device_name=d.get("device_name"),
#             device_model=d.get("device_model"),
#             battery_level=d.get("battery_level"),
#             device_status=status,
#             time_stamp=d.get("created_at")
#         ))

#     return response


# # --------------------------------------------------
# # GET SINGLE DEVICE (OWNER / ADMIN)
# # --------------------------------------------------
# @router.get("/by-device/{device_id}", response_model=DeviceOut)
# async def get_device_by_id(device_id: str, current_user: dict = Depends(get_current_user)):
#     device = await db.devices.find_one({"device_id": device_id})
#     if not device:
#         raise HTTPException(status_code=404, detail="Device not found")

#     if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")

#     status = calculate_status(device.get("last_seen"))

#     return DeviceOut(
#         id=str(device["_id"]),
#         device_id=device["device_id"],
#         device_name=device.get("device_name"),
#         device_model=device.get("device_model"),
#         battery_level=device.get("battery_level"),
#         device_status=status,        # ✅ FIXED (no undefined var)
#         time_stamp=device.get("created_at")
#     )


# # --------------------------------------------------
# # UPDATE DEVICE (METADATA ONLY)
# # --------------------------------------------------
# @router.put("/by-device/{device_id}", response_model=DeviceOut)
# async def update_device(device_id: str, updates: DeviceUpdate, current_user: dict = Depends(get_current_user)):
#     device = await db.devices.find_one({"device_id": device_id})
#     if not device:
#         raise HTTPException(status_code=404, detail="Device not found")

#     if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")

#     update_data = {k: v for k, v in updates.dict(exclude_unset=True).items()}

#     if "battery_level" in update_data and not (0 <= update_data["battery_level"] <= 100):
#         raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")

#     if not update_data:
#         raise HTTPException(status_code=400, detail="No valid fields provided")

#     await db.devices.update_one(
#         {"device_id": device_id},
#         {"$set": update_data}
#     )

#     device = await db.devices.find_one({"device_id": device_id})
#     status = calculate_status(device.get("last_seen"))

#     return DeviceOut(
#         id=str(device["_id"]),
#         device_id=device["device_id"],
#         device_name=device.get("device_name"),
#         device_model=device.get("device_model"),
#         battery_level=device.get("battery_level"),
#         device_status=status,
#         time_stamp=device.get("created_at")
#     )


# # --------------------------------------------------
# # DELETE DEVICE
# # --------------------------------------------------
# @router.delete("/by-device/{device_id}")
# async def delete_device(device_id: str, current_user: dict = Depends(get_current_user)):
#     device = await db.devices.find_one({"device_id": device_id})
#     if not device:
#         raise HTTPException(status_code=404, detail="Device not found")

#     if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")

#     await db.devices.delete_one({"device_id": device_id})
#     return {"message": f"Device '{device_id}' deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException
from app.schemas import DeviceCreate, DeviceOut, DeviceUpdate
from app.auth import require_role, get_current_user
from app.database import db
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

# --------------------------------------------------
# ONLINE / OFFLINE CONFIG
# --------------------------------------------------
OFFLINE_THRESHOLD = timedelta(minutes=5)


def calculate_status(last_seen: datetime | None) -> str:
    if not last_seen:
        return "offline"
    if datetime.utcnow() - last_seen <= OFFLINE_THRESHOLD:
        return "online"
    return "offline"


def resolve_timestamp(device: dict) -> datetime | None:
    """
    Prefer last_seen (MQTT driven),
    fallback to created_at (manual registration)
    """
    return device.get("last_seen") or device.get("created_at")


# --------------------------------------------------
# CREATE DEVICE (MANUAL REGISTRATION)
# --------------------------------------------------
@router.post("/", response_model=DeviceOut)
async def add_device(
    device: DeviceCreate,
    current_user: dict = Depends(get_current_user)
):
    existing_device = await db.devices.find_one({"device_id": device.device_id})
    if existing_device:
        raise HTTPException(status_code=400, detail="Device ID already exists")

    if device.battery_level is not None and not (0 <= device.battery_level <= 100):
        raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")

    now = datetime.utcnow()

    device_data = {
        "user_id": str(current_user["_id"]),
        "device_id": device.device_id,
        "device_name": device.device_name,
        "device_model": device.device_model,
        "battery_level": device.battery_level,
        "created_at": now,
        "last_seen": None  # updated only by MQTT
    }

    result = await db.devices.insert_one(device_data)

    return DeviceOut(
        id=str(result.inserted_id),
        device_id=device.device_id,
        device_name=device.device_name,
        device_model=device.device_model,
        battery_level=device.battery_level,
        device_status="offline",
        time_stamp=now
    )


# --------------------------------------------------
# GET ALL DEVICES (LOGGED-IN USER)
# --------------------------------------------------
@router.get("/", response_model=List[DeviceOut])
async def get_devices(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    devices = await db.devices.find({"user_id": user_id}).to_list(length=None)

    response = []
    for d in devices:
        last_seen = d.get("last_seen")
        status = calculate_status(last_seen)

        response.append(DeviceOut(
            id=str(d["_id"]),
            device_id=d["device_id"],
            device_name=d.get("device_name"),
            device_model=d.get("device_model"),
            battery_level=d.get("battery_level"),
            device_status=status,
            time_stamp=resolve_timestamp(d)
        ))

    return response


# --------------------------------------------------
# GET DEVICES BY USER (ADMIN)
# --------------------------------------------------
@router.get("/by-user/{user_id}", response_model=List[DeviceOut])
async def get_devices_by_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    devices = await db.devices.find({"user_id": user_id}).to_list(length=None)

    response = []
    for d in devices:
        status = calculate_status(d.get("last_seen"))

        response.append(DeviceOut(
            id=str(d["_id"]),
            device_id=d["device_id"],
            device_name=d.get("device_name"),
            device_model=d.get("device_model"),
            battery_level=d.get("battery_level"),
            device_status=status,
            time_stamp=resolve_timestamp(d)
        ))

    return response


# --------------------------------------------------
# GET SINGLE DEVICE (OWNER / ADMIN)
# --------------------------------------------------
@router.get("/by-device/{device_id}", response_model=DeviceOut)
async def get_device_by_id(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    device = await db.devices.find_one({"device_id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if (
        str(device["user_id"]) != str(current_user["_id"])
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    status = calculate_status(device.get("last_seen"))

    return DeviceOut(
        id=str(device["_id"]),
        device_id=device["device_id"],
        device_name=device.get("device_name"),
        device_model=device.get("device_model"),
        battery_level=device.get("battery_level"),
        device_status=status,
        time_stamp=resolve_timestamp(device)
    )


# --------------------------------------------------
# UPDATE DEVICE (METADATA ONLY)
# --------------------------------------------------
@router.put("/by-device/{device_id}", response_model=DeviceOut)
async def update_device(
    device_id: str,
    updates: DeviceUpdate,
    current_user: dict = Depends(get_current_user)
):
    device = await db.devices.find_one({"device_id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if (
        str(device["user_id"]) != str(current_user["_id"])
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = updates.dict(exclude_unset=True)

    if "battery_level" in update_data:
        if not (0 <= update_data["battery_level"] <= 100):
            raise HTTPException(status_code=400, detail="Battery level must be between 0 and 100")

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided")

    await db.devices.update_one(
        {"device_id": device_id},
        {"$set": update_data}
    )

    device = await db.devices.find_one({"device_id": device_id})
    status = calculate_status(device.get("last_seen"))

    return DeviceOut(
        id=str(device["_id"]),
        device_id=device["device_id"],
        device_name=device.get("device_name"),
        device_model=device.get("device_model"),
        battery_level=device.get("battery_level"),
        device_status=status,
        time_stamp=resolve_timestamp(device)
    )


# --------------------------------------------------
# DELETE DEVICE
# --------------------------------------------------
@router.delete("/by-device/{device_id}")
async def delete_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    device = await db.devices.find_one({"device_id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if (
        str(device["user_id"]) != str(current_user["_id"])
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.devices.delete_one({"device_id": device_id})
    return {"message": f"Device '{device_id}' deleted successfully"}
