#  app/routes/assets.py
from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_role, get_current_user
from app.database import db
from app.schemas import (
    AssetCreate, AssetOut, AssetUpdate, GeoPoint, 
    AssetWithDevicesOut, AssetDevicesResponse, LinkedDeviceInfo,
    LinkDeviceRequest, UpdateLinkStatusRequest, LinkResponse
)
from datetime import datetime
from typing import List, Optional, Any
from bson import ObjectId

router = APIRouter()

# @router.post("/", response_model=AssetOut)
# async def add_asset(asset: AssetCreate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Check for duplicate asset_id
#         existing_asset = await db["assets"].find_one({"asset_id": asset.asset_id})
#         if existing_asset:
#             raise HTTPException(status_code=400, detail="Asset ID already exists")
        
#         user_id = str(current_user["_id"])
#         current_time = datetime.utcnow()

#         asset_data = {
#             "user_id": user_id,
#             "asset_id": asset.asset_id,
#             "asset_name": asset.asset_name,
#             "asset_type": asset.asset_type,
#             "description": asset.description,
#             "registered_location": asset.registered_location.dict(),
#             "created_at": current_time,
#             "updated_at": current_time
#         }

#         result = await db["assets"].insert_one(asset_data)

#         # Return the created asset with the generated ID
#         return AssetOut(
#             id=str(result.inserted_id),
#             asset_id=asset.asset_id,
#             asset_name=asset.asset_name,
#             asset_type=asset.asset_type,
#             description=asset.description,
#             registered_location=asset.registered_location,
#             user_id=user_id,
#             created_at=current_time,
#             updated_at=current_time
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")

@router.post("/", response_model=AssetOut)
async def add_asset(asset: AssetCreate, current_user: dict = Depends(get_current_user)):
    try:
        # 1️⃣ Duplicate asset check
        existing_asset = await db["assets"].find_one({"asset_id": asset.asset_id})
        if existing_asset:
            raise HTTPException(status_code=400, detail="Asset ID already exists")

        # 2️⃣ 🔴 GEOFENCE VALIDATION (ADD HERE)
        geo = asset.registered_location

        if geo.radius is None or geo.radius <= 0:
            raise HTTPException(
                status_code=400,
                detail="Geofence radius must be greater than 0"
            )

        if geo.latitude < -90 or geo.latitude > 90:
            raise HTTPException(
                status_code=400,
                detail="Invalid geofence latitude"
            )

        if geo.longitude < -180 or geo.longitude > 180:
            raise HTTPException(
                status_code=400,
                detail="Invalid geofence longitude"
            )

        # 3️⃣ Normal flow continues
        user_id = str(current_user["_id"])
        current_time = datetime.utcnow()

        asset_data = {
            "user_id": user_id,
            "asset_id": asset.asset_id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "description": asset.description,
            "registered_location": geo.dict(),
            "created_at": current_time,
            "updated_at": current_time
        }

        result = await db["assets"].insert_one(asset_data)

        return AssetOut(
            id=str(result.inserted_id),
            asset_id=asset.asset_id,
            asset_name=asset.asset_name,
            asset_type=asset.asset_type,
            description=asset.description,
            registered_location=geo,
            user_id=user_id,
            created_at=current_time,
            updated_at=current_time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create asset: {str(e)}"
        )


# Get all assets for the current logged-in user
@router.get("/", response_model=List[AssetOut])
async def get_assets(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        cursor = db["assets"].find({"user_id": user_id})
        assets = await cursor.to_list(length=None)

        if not assets:
            return []  # Return empty list instead of 404 for better UX

        return [
            AssetOut(
                id=str(a["_id"]),
                asset_id=a["asset_id"],
                asset_name=a["asset_name"],
                asset_type=a["asset_type"],
                description=a.get("description"),
                registered_location=GeoPoint(**a["registered_location"]),
                user_id=a["user_id"],
                created_at=a["created_at"],
                updated_at=a["updated_at"]
            )
            for a in assets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")


# Get all assets for a specific user ID (admin only)
@router.get("/by-user/{user_id}", response_model=List[AssetOut])
async def get_assets_by_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
    try:
        print(f"Searching for assets with user_id: {user_id}")
        cursor = db["assets"].find({"user_id": user_id})
        assets = await cursor.to_list(length=None)

        if not assets:
            return []  # Return empty list for consistency

        return [
            AssetOut(
                id=str(a["_id"]),
                asset_id=a["asset_id"],
                asset_name=a["asset_name"],
                asset_type=a["asset_type"],
                description=a.get("description"),
                registered_location=GeoPoint(**a["registered_location"]),
                user_id=a["user_id"],
                created_at=a["created_at"],
                updated_at=a["updated_at"]
            )
            for a in assets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user assets: {str(e)}")


# Get a specific asset by asset_id
@router.get("/by-asset/{asset_id}", response_model=AssetOut)
async def get_asset_by_id(asset_id: str, current_user: dict = Depends(get_current_user)):
    try:
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

        # Allow admin users to access any asset
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")

        return AssetOut(
            id=str(asset["_id"]),
            asset_id=asset["asset_id"],
            asset_name=asset["asset_name"],
            asset_type=asset["asset_type"],
            description=asset.get("description"),
            registered_location=GeoPoint(**asset["registered_location"]),
            user_id=asset["user_id"],
            created_at=asset["created_at"],
            updated_at=asset["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset: {str(e)}")


# Update asset details
@router.put("/by-asset/{asset_id}", response_model=AssetOut)
async def update_asset(
    asset_id: str,
    updates: AssetUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Find the asset
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

        # Ensure user owns the asset or is admin
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this asset")

        # Convert updates to dict and remove None values
        update_data: dict[str, Any] = {
            k: v for k, v in updates.dict(exclude_unset=True).items() if v is not None
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        # Safely handle registered_location if it exists
        if "registered_location" in update_data:
            loc = update_data["registered_location"]
            # Only call .dict() if it's a Pydantic model
            if hasattr(loc, "dict"):
                update_data["registered_location"] = loc.dict()

        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Apply the update and return the updated document
        result = await db["assets"].find_one_and_update(
            {"asset_id": asset_id},
            {"$set": update_data},
            return_document=True
        )

        if not result:
            raise HTTPException(status_code=404, detail="Asset not found after update")

        # Return response as AssetOut
        return AssetOut(
            id=str(result["_id"]),
            asset_id=result["asset_id"],
            asset_name=result["asset_name"],
            asset_type=result["asset_type"],
            description=result.get("description"),
            registered_location=GeoPoint(**result["registered_location"]),
            user_id=result["user_id"],
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update asset: {str(e)}")

# @router.put("/by-asset/{asset_id}", response_model=AssetOut)
# async def update_asset(asset_id: str, updates: AssetUpdate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the asset
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

#         # Ensure user owns the asset or is admin
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to update this asset")

#         # Convert to dictionary and remove None values
#         update_data = {k: v for k, v in updates.dict(exclude_unset=True).items() if v is not None}

#         if not update_data:
#             raise HTTPException(status_code=400, detail="No valid fields provided for update")

#         # Handle registered_location separately if provided
#         if "registered_location" in update_data:
#             update_data["registered_location"] = update_data["registered_location"].dict()

#         # Update timestamp
#         update_data["updated_at"] = datetime.utcnow()

#         # Apply the update and return the updated document
#         result = await db["assets"].find_one_and_update(
#             {"asset_id": asset_id},
#             {"$set": update_data},
#             return_document=True
#         )

#         if not result:
#             raise HTTPException(status_code=404, detail="Asset not found after update")

#         return AssetOut(
#             id=str(result["_id"]),
#             asset_id=result["asset_id"],
#             asset_name=result["asset_name"],
#             asset_type=result["asset_type"],
#             description=result.get("description"),
#             registered_location=GeoPoint(**result["registered_location"]),
#             user_id=result["user_id"],
#             created_at=result["created_at"],
#             updated_at=result["updated_at"]
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update asset: {str(e)}")


# Update asset's registered location
@router.put("/by-asset/{asset_id}/location", response_model=AssetOut)
async def update_asset_location(asset_id: str, location: GeoPoint, current_user: dict = Depends(get_current_user)):
    try:
        # Find the asset
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

        # Ensure user owns the asset or is admin
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this asset")

        update_data = {
            "registered_location": location.dict(),
            "updated_at": datetime.utcnow()
        }

        # Apply the update and return the updated document
        result = await db["assets"].find_one_and_update(
            {"asset_id": asset_id},
            {"$set": update_data},
            return_document=True
        )

        return AssetOut(
            id=str(result["_id"]),
            asset_id=result["asset_id"],
            asset_name=result["asset_name"],
            asset_type=result["asset_type"],
            description=result.get("description"),
            registered_location=GeoPoint(**result["registered_location"]),
            user_id=result["user_id"],
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update asset location: {str(e)}")


@router.delete("/by-asset/{asset_id}")
async def delete_asset(asset_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Find the asset
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

        # Ensure user owns the asset or is admin
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this asset")

        # Delete all linked devices for this asset
        await db["asset_device_links"].delete_many({"asset_id": asset_id})

        # Delete the asset record
        result = await db["assets"].delete_one({"asset_id": asset_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Asset not found or already deleted")

        return {"message": f"Asset '{asset_id}' and all device links deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


# Get assets with device information
@router.get("/with-devices/", response_model=List[AssetWithDevicesOut])
async def get_assets_with_devices(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        # Build aggregation pipeline
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "asset_device_links",
                    "localField": "asset_id",
                    "foreignField": "asset_id",
                    "as": "links"
                }
            },
            {
                "$unwind": {
                    "path": "$links",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "links.device_id",
                    "foreignField": "device_id",
                    "as": "device_info"
                }
            },
            {
                "$unwind": {
                    "path": "$device_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "asset_id": {"$first": "$asset_id"},
                    "asset_name": {"$first": "$asset_name"},
                    "asset_type": {"$first": "$asset_type"},
                    "description": {"$first": "$description"},
                    "registered_location": {"$first": "$registered_location"},
                    "user_id": {"$first": "$user_id"},
                    "created_at": {"$first": "$created_at"},
                    "updated_at": {"$first": "$updated_at"},
                    "linked_devices": {
                        "$push": {
                            "device_id": "$device_info.device_id",
                            "device_name": "$device_info.device_name",
                            "device_model": "$device_info.device_model",
                            "battery_level": "$device_info.battery_level",
                            "device_status": "$device_info.device_status",
                            "link_status": "$links.status",
                            "linked_at": "$links.linked_at"
                        }
                    }
                }
            },
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "asset_id": 1,
                    "asset_name": 1,
                    "asset_type": 1,
                    "description": 1,
                    "registered_location": 1,
                    "user_id": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "linked_devices": {
                        "$cond": {
                            "if": {"$eq": [{"$size": "$linked_devices"}, 1]},
                            "then": {
                                "$cond": {
                                    "if": {"$eq": [{"$type": {"$arrayElemAt": ["$linked_devices.device_id", 0]}}, "null"]},
                                    "then": [],
                                    "else": "$linked_devices"
                                }
                            },
                            "else": "$linked_devices"
                        }
                    }
                }
            }
        ]

        # If admin, get all assets
        if current_user.get("role") == "admin":
            pipeline[0] = {"$match": {}}

        assets_with_devices = await db["assets"].aggregate(pipeline).to_list(length=None)
        
        # Convert to proper response model
        return [
            AssetWithDevicesOut(
                id=asset["id"],
                asset_id=asset["asset_id"],
                asset_name=asset["asset_name"],
                asset_type=asset["asset_type"],
                description=asset.get("description"),
                registered_location=GeoPoint(**asset["registered_location"]),
                user_id=asset["user_id"],
                created_at=asset["created_at"],
                updated_at=asset["updated_at"],
                linked_devices=asset.get("linked_devices", [])
            )
            for asset in assets_with_devices
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets with devices: {str(e)}")

@router.post("/link-device", response_model=LinkResponse)
async def link_device_to_asset(
    link_request: LinkDeviceRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        asset_id = link_request.asset_id
        device_id = link_request.device_id
        status = link_request.status

        # Check if asset exists
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Check if user owns the asset or is admin
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")

        # Check if device exists
        device = await db["devices"].find_one({"device_id": device_id})
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Check if user owns the device or is admin
        if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this device")

        # Check if asset is already linked to any device
        existing_asset_link = await db["asset_device_links"].find_one({"asset_id": asset_id})
        if existing_asset_link:
            raise HTTPException(
                status_code=400,
                detail="This asset is already linked to a device"
            )

        # Check if device is already linked to any asset
        existing_device_link = await db["asset_device_links"].find_one({"device_id": device_id})
        if existing_device_link:
            raise HTTPException(
                status_code=400,
                detail="This device is already linked to an asset"
            )

        # Create the link
        current_time = datetime.utcnow()
        link_data = {
            "asset_id": asset_id,
            "device_id": device_id,
            "status": status,
            "linked_at": current_time,
            "linked_by": str(current_user["_id"]),
            "updated_at": current_time
        }

        result = await db["asset_device_links"].insert_one(link_data)

        return LinkResponse(
            message="Device successfully linked to asset",
            link_id=str(result.inserted_id)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to link device to asset: {str(e)}")
# # Link device to asset
# @router.post("/link-device", response_model=LinkResponse)
# async def link_device_to_asset(
#     link_request: LinkDeviceRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     try:
#         asset_id = link_request.asset_id
#         device_id = link_request.device_id
#         status = link_request.status
        
#         # Check if asset exists and user has access
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail="Asset not found")
        
#         # Check if user owns the asset or is admin
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to access this asset")
        
#         # Check if device exists
#         device = await db["devices"].find_one({"device_id": device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail="Device not found")
        
#         # Check if user owns the device or is admin
#         if str(device["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to access this device")
        
#         # Check if link already exists
#         existing_link = await db["asset_device_links"].find_one({
#             "asset_id": asset_id,
#             "device_id": device_id
#         })
#         if existing_link:
#             raise HTTPException(status_code=400, detail="Device is already linked to this asset")
        
#         # Create the link
#         current_time = datetime.utcnow()
#         link_data = {
#             "asset_id": asset_id,
#             "device_id": device_id,
#             "status": status,
#             "linked_at": current_time,
#             "linked_by": str(current_user["_id"]),
#             "updated_at": current_time
#         }
        
#         result = await db["asset_device_links"].insert_one(link_data)
        
#         return LinkResponse(
#             message="Device successfully linked to asset", 
#             link_id=str(result.inserted_id)
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to link device to asset: {str(e)}")


# Unlink device from asset
@router.delete("/unlink-device")
async def unlink_device_from_asset(
    asset_id: str, 
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if asset exists and user has access
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
            
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")
        
        # Delete the link
        result = await db["asset_device_links"].delete_one({
            "asset_id": asset_id,
            "device_id": device_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return {"message": "Device successfully unlinked from asset"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlink device from asset: {str(e)}")


# Get devices linked to an asset
@router.get("/{asset_id}/devices", response_model=AssetDevicesResponse)
async def get_devices_by_asset(asset_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Check if asset exists and user has access
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
            
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")
        
        # Get all device links for this asset
        links_cursor = db["asset_device_links"].find({"asset_id": asset_id})
        links = await links_cursor.to_list(length=None)
        
        if not links:
            return AssetDevicesResponse(linked_devices=[])
        
        # Get detailed device information for each linked device
        device_ids = [link["device_id"] for link in links]
        devices_cursor = db["devices"].find({"device_id": {"$in": device_ids}})
        devices = await devices_cursor.to_list(length=None)
        
        # Combine device info with link info
        linked_devices = []
        for link in links:
            device = next((d for d in devices if d["device_id"] == link["device_id"]), None)
            if device:
                linked_devices.append(
                    LinkedDeviceInfo(
                        device_id=device["device_id"],
                        device_name=device.get("device_name"),
                        device_model=device.get("device_model"),
                        battery_level=device.get("battery_level"),
                        device_status=device.get("device_status"),
                        link_status=link["status"],
                        linked_at=link["linked_at"]
                    )
                )
        
        return AssetDevicesResponse(linked_devices=linked_devices)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch devices for asset: {str(e)}")


# Update link status
@router.put("/link-status")
async def update_link_status(
    update_request: UpdateLinkStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        asset_id = update_request.asset_id
        device_id = update_request.device_id
        status = update_request.status
        
        # Check if asset exists and user has access
        asset = await db["assets"].find_one({"asset_id": asset_id})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
            
        if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access this asset")
        
        # Update the link status
        result = await db["asset_device_links"].update_one(
            {"asset_id": asset_id, "device_id": device_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return {"message": "Link status updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update link status: {str(e)}")


# from fastapi import APIRouter, Depends, HTTPException
# from app.schemas import AssetCreate, AssetOut, AssetUpdate, GeoPoint
# from app.auth import require_role, get_current_user
# from app.database import db
# from datetime import datetime
# from typing import List
# from bson import ObjectId

# router = APIRouter()

# @router.post("/", response_model=AssetOut)
# async def add_asset(asset: AssetCreate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Check for duplicate asset_id
#         existing_asset = await db["assets"].find_one({"asset_id": asset.asset_id})
#         if existing_asset:
#             raise HTTPException(status_code=400, detail="Asset ID already exists")
        
#         # Check if device exists
#         device = await db["devices"].find_one({"device_id": asset.device_id})
#         if not device:
#             raise HTTPException(status_code=404, detail="Device not found")
        
#         # Check if device is already assigned to another asset
#         existing_asset_with_device = await db["assets"].find_one({"device_id": asset.device_id})
#         if existing_asset_with_device:
#             raise HTTPException(status_code=400, detail="Device is already assigned to another asset")
        
#         # Verify user owns the device (unless admin)
#         if (str(device["user_id"]) != str(current_user["_id"]) and 
#             current_user.get("role") != "admin"):
#             raise HTTPException(status_code=403, detail="Not authorized to use this device")
        
#         user_id = str(current_user["_id"])
#         current_time = datetime.utcnow()

#         asset_data = {
#             "user_id": user_id,
#             "asset_id": asset.asset_id,
#             "asset_name": asset.asset_name,
#             "asset_type": asset.asset_type,
#             "description": asset.description,
#             "device_id": asset.device_id,
#             "registered_location": asset.registered_location.dict(),
#             "created_at": current_time,
#             "updated_at": current_time
#         }

#         result = await db["assets"].insert_one(asset_data)

#         # Return the created asset with the generated ID
#         return AssetOut(
#             id=str(result.inserted_id),
#             asset_id=asset.asset_id,
#             asset_name=asset.asset_name,
#             asset_type=asset.asset_type,
#             description=asset.description,
#             device_id=asset.device_id,
#             registered_location=asset.registered_location,
#             user_id=user_id,
#             created_at=current_time,
#             updated_at=current_time
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")


# # Get all assets for the current logged-in user
# @router.get("/", response_model=List[AssetOut])
# async def get_assets(current_user: dict = Depends(get_current_user)):
#     try:
#         user_id = str(current_user["_id"])
#         cursor = db["assets"].find({"user_id": user_id})
#         assets = await cursor.to_list(length=None)

#         if not assets:
#             return []  # Return empty list instead of 404 for better UX

#         return [
#             AssetOut(
#                 id=str(a["_id"]),
#                 asset_id=a["asset_id"],
#                 asset_name=a["asset_name"],
#                 asset_type=a["asset_type"],
#                 description=a.get("description"),
#                 device_id=a["device_id"],
#                 registered_location=GeoPoint(**a["registered_location"]),
#                 user_id=a["user_id"],
#                 created_at=a["created_at"],
#                 updated_at=a["updated_at"]
#             )
#             for a in assets
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")


# # Get all assets for a specific user ID (admin only)
# @router.get("/by-user/{user_id}", response_model=List[AssetOut])
# async def get_assets_by_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
#     try:
#         print(f"Searching for assets with user_id: {user_id}")
#         cursor = db["assets"].find({"user_id": user_id})
#         assets = await cursor.to_list(length=None)

#         if not assets:
#             return []  # Return empty list for consistency

#         return [
#             AssetOut(
#                 id=str(a["_id"]),
#                 asset_id=a["asset_id"],
#                 asset_name=a["asset_name"],
#                 asset_type=a["asset_type"],
#                 description=a.get("description"),
#                 device_id=a["device_id"],
#                 registered_location=GeoPoint(**a["registered_location"]),
#                 user_id=a["user_id"],
#                 created_at=a["created_at"],
#                 updated_at=a["updated_at"]
#             )
#             for a in assets
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch user assets: {str(e)}")


# # Get a specific asset by asset_id
# @router.get("/by-asset/{asset_id}", response_model=AssetOut)
# async def get_asset_by_id(asset_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

#         # Allow admin users to access any asset
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to access this asset")

#         return AssetOut(
#             id=str(asset["_id"]),
#             asset_id=asset["asset_id"],
#             asset_name=asset["asset_name"],
#             asset_type=asset["asset_type"],
#             description=asset.get("description"),
#             device_id=asset["device_id"],
#             registered_location=GeoPoint(**asset["registered_location"]),
#             user_id=asset["user_id"],
#             created_at=asset["created_at"],
#             updated_at=asset["updated_at"]
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch asset: {str(e)}")


# # Get asset by device_id
# @router.get("/by-device/{device_id}", response_model=AssetOut)
# async def get_asset_by_device(device_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         asset = await db["assets"].find_one({"device_id": device_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"No asset found for device ID {device_id}")

#         # Allow admin users to access any asset
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to access this asset")

#         return AssetOut(
#             id=str(asset["_id"]),
#             asset_id=asset["asset_id"],
#             asset_name=asset["asset_name"],
#             asset_type=asset["asset_type"],
#             description=asset.get("description"),
#             device_id=asset["device_id"],
#             registered_location=GeoPoint(**asset["registered_location"]),
#             user_id=asset["user_id"],
#             created_at=asset["created_at"],
#             updated_at=asset["updated_at"]
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch asset by device: {str(e)}")


# # Update asset details
# @router.put("/by-asset/{asset_id}", response_model=AssetOut)
# async def update_asset(asset_id: str, updates: AssetUpdate, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the asset
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

#         # Ensure user owns the asset or is admin
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to update this asset")

#         # Convert to dictionary and remove None values
#         update_data = {k: v for k, v in updates.dict(exclude_unset=True).items() if v is not None}
        
#         # If device_id is being updated, check if new device exists and is available
#         if "device_id" in update_data:
#             new_device = await db["devices"].find_one({"device_id": update_data["device_id"]})
#             if not new_device:
#                 raise HTTPException(status_code=404, detail="New device not found")
            
#             # Check if new device is already assigned to another asset (excluding current asset)
#             existing_asset_with_device = await db["assets"].find_one({
#                 "device_id": update_data["device_id"],
#                 "asset_id": {"$ne": asset_id}  # Exclude current asset
#             })
#             if existing_asset_with_device:
#                 raise HTTPException(status_code=400, detail="New device is already assigned to another asset")
            
#             # Verify user owns the new device (unless admin)
#             if (str(new_device["user_id"]) != str(current_user["_id"]) and 
#                 current_user.get("role") != "admin"):
#                 raise HTTPException(status_code=403, detail="Not authorized to use this device")

#         if not update_data:
#             raise HTTPException(status_code=400, detail="No valid fields provided for update")

#         # Update timestamp
#         update_data["updated_at"] = datetime.utcnow()

#         # Apply the update and return the updated document
#         result = await db["assets"].find_one_and_update(
#             {"asset_id": asset_id},
#             {"$set": update_data},
#             return_document=True
#         )

#         if not result:
#             raise HTTPException(status_code=404, detail="Asset not found after update")

#         return AssetOut(
#             id=str(result["_id"]),
#             asset_id=result["asset_id"],
#             asset_name=result["asset_name"],
#             asset_type=result["asset_type"],
#             description=result.get("description"),
#             device_id=result["device_id"],
#             registered_location=GeoPoint(**result["registered_location"]),
#             user_id=result["user_id"],
#             created_at=result["created_at"],
#             updated_at=result["updated_at"]
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update asset: {str(e)}")


# # Update asset's registered location
# @router.put("/by-asset/{asset_id}/location", response_model=AssetOut)
# async def update_asset_location(asset_id: str, location: GeoPoint, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the asset
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

#         # Ensure user owns the asset or is admin
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to update this asset")

#         update_data = {
#             "registered_location": location.dict(),
#             "updated_at": datetime.utcnow()
#         }

#         # Apply the update and return the updated document
#         result = await db["assets"].find_one_and_update(
#             {"asset_id": asset_id},
#             {"$set": update_data},
#             return_document=True
#         )

#         return AssetOut(
#             id=str(result["_id"]),
#             asset_id=result["asset_id"],
#             asset_name=result["asset_name"],
#             asset_type=result["asset_type"],
#             description=result.get("description"),
#             device_id=result["device_id"],
#             registered_location=GeoPoint(**result["registered_location"]),
#             user_id=result["user_id"],
#             created_at=result["created_at"],
#             updated_at=result["updated_at"]
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update asset location: {str(e)}")


# @router.delete("/by-asset/{asset_id}")
# async def delete_asset(asset_id: str, current_user: dict = Depends(get_current_user)):
#     try:
#         # Find the asset
#         asset = await db["assets"].find_one({"asset_id": asset_id})
#         if not asset:
#             raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")

#         # Ensure user owns the asset or is admin
#         if str(asset["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Not authorized to delete this asset")

#         # Delete the record
#         result = await db["assets"].delete_one({"asset_id": asset_id})

#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="Asset not found or already deleted")

#         return {"message": f"Asset '{asset_id}' deleted successfully"}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


# # Get assets with device information
# @router.get("/with-devices/", response_model=List[dict])
# async def get_assets_with_devices(current_user: dict = Depends(get_current_user)):
#     try:
#         user_id = str(current_user["_id"])
        
#         # Build aggregation pipeline
#         pipeline = [
#             {"$match": {"user_id": user_id}},
#             {
#                 "$lookup": {
#                     "from": "devices",
#                     "localField": "device_id",
#                     "foreignField": "device_id",
#                     "as": "device_info"
#                 }
#             },
#             {
#                 "$unwind": {
#                     "path": "$device_info",
#                     "preserveNullAndEmptyArrays": True
#                 }
#             },
#             {
#                 "$project": {
#                     "id": {"$toString": "$_id"},
#                     "asset_id": 1,
#                     "asset_name": 1,
#                     "asset_type": 1,
#                     "description": 1,
#                     "device_id": 1,
#                     "registered_location": 1,
#                     "created_at": 1,
#                     "updated_at": 1,
#                     "device_info": {
#                         "device_name": "$device_info.device_name",
#                         "device_model": "$device_info.device_model",
#                         "battery_level": "$device_info.battery_level",
#                         "device_status": "$device_info.device_status",
#                         "last_seen": "$device_info.time_stamp"
#                     }
#                 }
#             }
#         ]

#         # If admin, get all assets
#         if current_user.get("role") == "admin":
#             pipeline[0] = {"$match": {}}

#         assets_with_devices = await db["assets"].aggregate(pipeline).to_list(length=None)
        
#         return assets_with_devices

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch assets with devices: {str(e)}")


