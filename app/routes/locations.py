# from fastapi import APIRouter, Depends, HTTPException
# from datetime import datetime
# from math import radians, sin, cos, sqrt, atan2
# from typing import List
# from app.schemas import LocationIn, LocationOut
# from app.auth import get_current_user
# from app.database import db
# from bson import ObjectId

# router = APIRouter()


# # --- Haversine Distance (in meters) ---
# def calculate_distance(lat1, lon1, lat2, lon2):
#     R = 6371000  # Earth radius in meters
#     phi1, phi2 = radians(lat1), radians(lat2)
#     dphi = radians(lat2 - lat1)
#     dlambda = radians(lon2 - lon1)

#     a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
#     c = 2 * atan2(sqrt(a), sqrt(1 - a))
#     return R * c


# # --- Add new location ---
# @router.post("/", response_model=LocationOut)
# async def add_location(location: LocationIn, current_user: dict = Depends(get_current_user)):
#     try:
#         # Step 1: Validate Device
#         device = await db["devices"].find_one({"device_id": location.device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail="Device not found")

#         # Step 2: Get last known location (if any)
#         last_location = await db["locations"].find_one(
#             {"device_id": location.device_id}, sort=[("timestamp", -1)]
#         )

#         distance_moved = 0.0
#         movement_status = "stationary"
#         alert_message = None

#         if last_location:
#             distance_moved = calculate_distance(
#                 last_location["latitude"],
#                 last_location["longitude"],
#                 location.latitude,
#                 location.longitude,
#             )

#             # Step 3: Check movement threshold
#             if distance_moved < 10:
#                 movement_status = "stationary"
#             elif 10 <= distance_moved < 100:
#                 movement_status = "moving slowly"
#             else:
#                 movement_status = "moving fast"

#             # Step 4: Alert logic (example: sudden jump)
#             if distance_moved > 1000:
#                 alert_message = f"⚠️ Sudden movement detected ({distance_moved:.1f} m)"

#         # Step 5: Save location to DB
#         loc_doc = {
#             "device_id": location.device_id,
#             "latitude": location.latitude,
#             "longitude": location.longitude,
#             "timestamp": location.timestamp or datetime.utcnow(),
#             "distance_moved": distance_moved,
#             "movement_status": movement_status,
#             "alert_message": alert_message,
#         }

#         result = await db["locations"].insert_one(loc_doc)

#         return LocationOut(
#             id=str(result.inserted_id),
#             device_id=location.device_id,
#             latitude=location.latitude,
#             longitude=location.longitude,
#             timestamp=loc_doc["timestamp"],
#             distance_moved=distance_moved,
#             movement_status=movement_status,
#             alert_message=alert_message,
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to add location: {str(e)}")


# # --- Get all locations for current user ---
# @router.get("/", response_model=List[LocationOut])
# async def get_all_locations(current_user: dict = Depends(get_current_user)):
#     try:
#         user_id = str(current_user["_id"])
#         devices = await db["devices"].find({"user_id": user_id}).to_list(length=None)
#         device_ids = [d["device_id"] for d in devices]

#         cursor = db["locations"].find({"device_id": {"$in": device_ids}})
#         locations = await cursor.to_list(length=None)

#         return [
#             LocationOut(
#                 id=str(l["_id"]),
#                 device_id=l["device_id"],
#                 latitude=l["latitude"],
#                 longitude=l["longitude"],
#                 timestamp=l["timestamp"],
#                 distance_moved=l.get("distance_moved", 0.0),
#                 movement_status=l.get("movement_status", "unknown"),
#                 alert_message=l.get("alert_message"),
#             )
#             for l in locations
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import get_current_user, require_role
from app.database import db
from app.schemas import (
    LocationUpdate, LocationOut, GeoPoint, 
    AssetLocationHistory, DeviceLocationHistory,
    LocationBulkUpdate
)
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId

router = APIRouter()

# Update asset location
@router.put("/assets/{asset_id}/location", response_model=LocationOut)
async def update_asset_location(
    asset_id: str,
    location: LocationUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if asset exists and user has access
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this asset")

        current_time = datetime.utcnow()
        
        # Update asset's current location
        await db["assets"].update_one(
            {"asset_id": asset_id},
            {"$set": {
                "registered_location": location.location.dict(),
                "updated_at": current_time
            }}
        )
        
        # Store location in history
        location_data = {
            "asset_id": asset_id,
            "location": location.location.dict(),
            "timestamp": current_time,
            "source": location.source,
            "accuracy": location.accuracy,
            "recorded_by": str(current_user["_id"])
        }
        
        result = await db["asset_location_history"].insert_one(location_data)
        
        return LocationOut(
            id=str(result.inserted_id),
            asset_id=asset_id,
            location=location.location,
            timestamp=current_time,
            source=location.source,
            accuracy=location.accuracy
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update asset location: {str(e)}")

# Update device location
@router.put("/devices/{device_id}/location", response_model=LocationOut)
async def update_device_location(
    device_id: str,
    location: LocationUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if device exists and user has access
        device = await db["devices"].find_one({"device_id": device_id})
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this device")

        current_time = datetime.utcnow()
        
        # Store location in device location history
        location_data = {
            "device_id": device_id,
            "location": location.location.dict(),
            "timestamp": current_time,
            "source": location.source,
            "accuracy": location.accuracy,
            "recorded_by": str(current_user["_id"])
        }
        
        result = await db["device_location_history"].insert_one(location_data)
        
        return LocationOut(
            id=str(result.inserted_id),
            device_id=device_id,
            location=location.location,
            timestamp=current_time,
            source=location.source,
            accuracy=location.accuracy
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update device location: {str(e)}")

# Bulk update locations for multiple assets/devices
@router.post("/bulk-update")
async def bulk_update_locations(
    updates: LocationBulkUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        current_time = datetime.utcnow()
        results = {
            "updated_assets": 0,
            "updated_devices": 0,
            "errors": []
        }
        
        # Update asset locations
        for asset_update in updates.assets:
            try:
                asset = await db["assets"].find_one({"asset_id": asset_update.asset_id})
                if not asset:
                    results["errors"].append(f"Asset {asset_update.asset_id} not found")
                    continue
                
                if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
                    results["errors"].append(f"Not authorized to update asset {asset_update.asset_id}")
                    continue
                
                # Update asset location
                await db["assets"].update_one(
                    {"asset_id": asset_update.asset_id},
                    {"$set": {
                        "registered_location": asset_update.location.dict(),
                        "updated_at": current_time
                    }}
                )
                
                # Store in history
                await db["asset_location_history"].insert_one({
                    "asset_id": asset_update.asset_id,
                    "location": asset_update.location.dict(),
                    "timestamp": current_time,
                    "source": asset_update.source,
                    "accuracy": asset_update.accuracy,
                    "recorded_by": str(current_user["_id"])
                })
                
                results["updated_assets"] += 1
                
            except Exception as e:
                results["errors"].append(f"Error updating asset {asset_update.asset_id}: {str(e)}")
        
        # Update device locations
        for device_update in updates.devices:
            try:
                device = await db["devices"].find_one({"device_id": device_update.device_id})
                if not device:
                    results["errors"].append(f"Device {device_update.device_id} not found")
                    continue
                
                if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
                    results["errors"].append(f"Not authorized to update device {device_update.device_id}")
                    continue
                
                # Store in device location history
                await db["device_location_history"].insert_one({
                    "device_id": device_update.device_id,
                    "location": device_update.location.dict(),
                    "timestamp": current_time,
                    "source": device_update.source,
                    "accuracy": device_update.accuracy,
                    "recorded_by": str(current_user["_id"])
                })
                
                results["updated_devices"] += 1
                
            except Exception as e:
                results["errors"].append(f"Error updating device {device_update.device_id}: {str(e)}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform bulk location update: {str(e)}")

# Get asset location history
@router.get("/assets/{asset_id}/history", response_model=List[AssetLocationHistory])
async def get_asset_location_history(
    asset_id: str,
    days: int = Query(7, description="Number of days of history to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if asset exists and user has access
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")

        # Calculate start date
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get location history
        cursor = db["asset_location_history"].find({
            "asset_id": asset_id,
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1)
        
        history = await cursor.to_list(length=None)
        
        return [
            AssetLocationHistory(
                id=str(item["_id"]),
                asset_id=item["asset_id"],
                location=GeoPoint(**item["location"]),
                timestamp=item["timestamp"],
                source=item.get("source"),
                accuracy=item.get("accuracy")
            )
            for item in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset location history: {str(e)}")

# Get device location history
@router.get("/devices/{device_id}/history", response_model=List[DeviceLocationHistory])
async def get_device_location_history(
    device_id: str,
    days: int = Query(7, description="Number of days of history to retrieve"),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if device exists and user has access
        device = await db["devices"].find_one({"device_id": device_id})
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this device")

        # Calculate start date
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get location history
        cursor = db["device_location_history"].find({
            "device_id": device_id,
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1)
        
        history = await cursor.to_list(length=None)
        
        return [
            DeviceLocationHistory(
                id=str(item["_id"]),
                device_id=item["device_id"],
                location=GeoPoint(**item["location"]),
                timestamp=item["timestamp"],
                source=item.get("source"),
                accuracy=item.get("accuracy")
            )
            for item in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch device location history: {str(e)}")

# Get current locations for all user's assets
@router.get("/assets/current", response_model=List[AssetLocationHistory])
async def get_current_asset_locations(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        # Get user's assets
        assets_cursor = db["assets"].find({"user_id": user_id})
        assets = await assets_cursor.to_list(length=None)
        
        if not assets:
            return []
        
        # Get latest location for each asset
        current_locations = []
        for asset in assets:
            latest_location = await db["asset_location_history"].find_one(
                {"asset_id": asset["asset_id"]},
                sort=[("timestamp", -1)]
            )
            
            if latest_location:
                current_locations.append(
                    AssetLocationHistory(
                        id=str(latest_location["_id"]),
                        asset_id=latest_location["asset_id"],
                        location=GeoPoint(**latest_location["location"]),
                        timestamp=latest_location["timestamp"],
                        source=latest_location.get("source"),
                        accuracy=latest_location.get("accuracy")
                    )
                )
            else:
                # Fallback to registered location if no history
                current_locations.append(
                    AssetLocationHistory(
                        id=str(asset["_id"]),
                        asset_id=asset["asset_id"],
                        location=GeoPoint(**asset["registered_location"]),
                        timestamp=asset.get("updated_at", asset["created_at"]),
                        source="registered",
                        accuracy=None
                    )
                )
        
        return current_locations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current asset locations: {str(e)}")

# Get assets within geographic boundary
@router.get("/assets/within-boundary")
async def get_assets_within_boundary(
    min_lat: float = Query(..., description="Minimum latitude"),
    max_lat: float = Query(..., description="Maximum latitude"),
    min_lng: float = Query(..., description="Minimum longitude"),
    max_lng: float = Query(..., description="Maximum longitude"),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = str(current_user["_id"])
        
        # Build aggregation pipeline to get latest locations
        pipeline = [
            # Get user's assets
            {"$match": {"user_id": user_id}},
            # Lookup latest location
            {
                "$lookup": {
                    "from": "asset_location_history",
                    "let": {"asset_id": "$asset_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$asset_id", "$$asset_id"]}}},
                        {"$sort": {"timestamp": -1}},
                        {"$limit": 1}
                    ],
                    "as": "latest_location"
                }
            },
            # Use latest location or fallback to registered location
            {
                "$project": {
                    "asset_id": 1,
                    "asset_name": 1,
                    "asset_type": 1,
                    "current_location": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$latest_location"}, 0]},
                            "then": {"$arrayElemAt": ["$latest_location.location", 0]},
                            "else": "$registered_location"
                        }
                    },
                    "timestamp": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$latest_location"}, 0]},
                            "then": {"$arrayElemAt": ["$latest_location.timestamp", 0]},
                            "else": "$updated_at"
                        }
                    }
                }
            },
            # Filter by geographic boundary
            {
                "$match": {
                    "current_location.latitude": {"$gte": min_lat, "$lte": max_lat},
                    "current_location.longitude": {"$gte": min_lng, "$lte": max_lng}
                }
            }
        ]
        
        # If admin, get all assets
        if current_user.get("role") == "admin":
            pipeline[0] = {"$match": {}}
        
        assets_in_boundary = await db["assets"].aggregate(pipeline).to_list(length=None)
        
        return [
            {
                "asset_id": asset["asset_id"],
                "asset_name": asset["asset_name"],
                "asset_type": asset["asset_type"],
                "location": GeoPoint(**asset["current_location"]),
                "timestamp": asset["timestamp"]
            }
            for asset in assets_in_boundary
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets within boundary: {str(e)}")