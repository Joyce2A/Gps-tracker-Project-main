from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user, require_role
from app.database import db
from app.schemas import (
    DashboardStats, AssetStatusSummary, DeviceStatusSummary,
    RecentActivity, AlertSummary
)
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bson import ObjectId

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        current_time = datetime.utcnow()
        
        # Base query for user-specific data
        user_query = {"user_id": user_id}
        
        # If admin, get all data
        if current_user.get("role") == "admin":
            user_query = {}

        # Get asset statistics
        total_assets = await db["assets"].count_documents(user_query)
        
        assets_by_type = await db["assets"].aggregate([
            {"$match": user_query},
            {"$group": {"_id": "$asset_type", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        def _key_str(k):
            return str(k) if k is not None else "unknown"

        assets_by_type_dict = {
            _key_str(item.get("_id")): item.get("count", 0)
            for item in assets_by_type
        }

        # Get device statistics
        total_devices = await db["devices"].count_documents(user_query)
        
        devices_by_status = await db["devices"].aggregate([
            {"$match": user_query},
            {"$group": {"_id": "$device_status", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        devices_by_status_dict = {
            _key_str(item.get("_id")): item.get("count", 0)
            for item in devices_by_status
        }

        # Get alert statistics
        alert_stats = await db["alerts"].aggregate([
            {"$match": {**user_query, "created_at": {"$gte": current_time - timedelta(days=30)}}},
            {
                "$facet": {
                    "total_alerts": [{"$count": "count"}],
                    "alerts_by_severity": [{"$group": {"_id": "$severity", "count": {"$sum": 1}}}],
                    "open_alerts": [{"$match": {"status": "open"}}, {"$count": "count"}]
                }
            }
        ]).to_list(length=None)

        alert_data = alert_stats[0] if alert_stats else {}
        
        total_alerts = alert_data.get("total_alerts", [{}])[0].get("count", 0) if alert_data.get("total_alerts") else 0
        open_alerts = alert_data.get("open_alerts", [{}])[0].get("count", 0) if alert_data.get("open_alerts") else 0
        
        alerts_by_severity = {
            _key_str(item.get("_id")): item.get("count", 0)
            for item in alert_data.get("alerts_by_severity", [])
        }

        # Get linked devices count
        linked_devices_pipeline = [
            {"$match": user_query},
            {
                "$lookup": {
                    "from": "asset_device_links",
                    "localField": "asset_id",
                    "foreignField": "asset_id",
                    "as": "links"
                }
            },
            {"$unwind": "$links"},
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        
        if current_user.get("role") == "admin":
            linked_devices_pipeline[0] = {"$match": {}}
            
        linked_devices_result = await db["assets"].aggregate(linked_devices_pipeline).to_list(length=None)
        linked_devices_count = linked_devices_result[0]["count"] if linked_devices_result else 0

        return DashboardStats(
            total_assets=total_assets,
            total_devices=total_devices,
            total_alerts=total_alerts,
            open_alerts=open_alerts,
            linked_devices_count=linked_devices_count,
            assets_by_type=assets_by_type_dict,
            devices_by_status=devices_by_status_dict,
            alerts_by_severity=alerts_by_severity
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@router.get("/asset-status-summary", response_model=AssetStatusSummary)
async def get_asset_status_summary(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        # Base query for user-specific data
        user_query = {"user_id": user_id}
        
        # If admin, get all data
        if current_user.get("role") == "admin":
            user_query = {}

        # Get assets with their linked devices and status
        pipeline = [
            {"$match": user_query},
            {
                "$lookup": {
                    "from": "asset_device_links",
                    "localField": "asset_id",
                    "foreignField": "asset_id",
                    "as": "device_links"
                }
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "device_links.device_id",
                    "foreignField": "device_id",
                    "as": "linked_devices"
                }
            },
            {
                "$project": {
                    "asset_id": 1,
                    "asset_name": 1,
                    "asset_type": 1,
                    "linked_devices_count": {"$size": "$device_links"},
                    "online_devices_count": {
                        "$size": {
                            "$filter": {
                                "input": "$linked_devices",
                                "as": "device",
                                "cond": {"$eq": ["$$device.device_status", "online"]}
                            }
                        }
                    },
                    "offline_devices_count": {
                        "$size": {
                            "$filter": {
                                "input": "$linked_devices",
                                "as": "device",
                                "cond": {"$eq": ["$$device.device_status", "offline"]}
                            }
                        }
                    }
                }
            }
        ]

        assets_with_status = await db["assets"].aggregate(pipeline).to_list(length=None)
        
        # Calculate summary statistics
        total_assets = len(assets_with_status)
        assets_with_devices = sum(1 for asset in assets_with_status if asset["linked_devices_count"] > 0)
        assets_without_devices = total_assets - assets_with_devices
        assets_online = sum(1 for asset in assets_with_status if asset["online_devices_count"] > 0)
        assets_offline = total_assets - assets_online
        
        # Calculate assets by type
        assets_by_type = {}
        for asset in assets_with_status:
            asset_type = asset["asset_type"]
            assets_by_type[asset_type] = assets_by_type.get(asset_type, 0) + 1

        return AssetStatusSummary(
            total_assets=total_assets,
            assets_with_devices=assets_with_devices,
            assets_without_devices=assets_without_devices,
            assets_online=assets_online,
            assets_offline=assets_offline,
            assets_by_type=assets_by_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset status summary: {str(e)}")