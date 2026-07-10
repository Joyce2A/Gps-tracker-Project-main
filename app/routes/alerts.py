from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import get_current_user, require_role
from app.database import db
from app.schemas import (
    AlertCreate, AlertOut, AlertUpdate, 
    AlertRuleCreate, AlertRuleOut, AlertRuleUpdate,
    AlertSummary
)
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
import asyncio

router = APIRouter()

# Create a new alert rule
@router.post("/rules", response_model=AlertRuleOut)
async def create_alert_rule(
    rule: AlertRuleCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = str(current_user["_id"])
        current_time = datetime.utcnow()

        rule_data = {
            "user_id": user_id,
            "name": rule.name,
            "description": rule.description,
            "alert_type": rule.alert_type,
            "conditions": rule.conditions.dict(),
            "is_active": rule.is_active,
            "severity": rule.severity,
            "notification_channels": rule.notification_channels,
            "created_at": current_time,
            "updated_at": current_time
        }

        result = await db["alert_rules"].insert_one(rule_data)

        return AlertRuleOut(
            id=str(result.inserted_id),
            **rule_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")

# Get all alert rules for current user
@router.get("/rules", response_model=List[AlertRuleOut])
async def get_alert_rules(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        cursor = db["alert_rules"].find({"user_id": user_id})
        rules = await cursor.to_list(length=None)

        return [
            AlertRuleOut(
                id=str(rule["_id"]),
                user_id=rule["user_id"],
                name=rule["name"],
                description=rule.get("description"),
                alert_type=rule["alert_type"],
                conditions=rule["conditions"],
                is_active=rule["is_active"],
                severity=rule["severity"],
                notification_channels=rule.get("notification_channels", []),
                created_at=rule["created_at"],
                updated_at=rule["updated_at"]
            )
            for rule in rules
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alert rules: {str(e)}")

# Update alert rule
@router.put("/rules/{rule_id}", response_model=AlertRuleOut)
async def update_alert_rule(
    rule_id: str,
    updates: AlertRuleUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if rule exists and user has access
        rule = await db["alert_rules"].find_one({"_id": ObjectId(rule_id)})
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        if str(rule["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this rule")

        # Convert to dictionary and remove None values
        update_data = {k: v for k, v in updates.dict(exclude_unset=True).items() if v is not None}
        
        if "conditions" in update_data:
            update_data["conditions"] = update_data["conditions"].dict()

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        update_data["updated_at"] = datetime.utcnow()

        result = await db["alert_rules"].find_one_and_update(
            {"_id": ObjectId(rule_id)},
            {"$set": update_data},
            return_document=True
        )

        return AlertRuleOut(
            id=str(result["_id"]),
            user_id=result["user_id"],
            name=result["name"],
            description=result.get("description"),
            alert_type=result["alert_type"],
            conditions=result["conditions"],
            is_active=result["is_active"],
            severity=result["severity"],
            notification_channels=result.get("notification_channels", []),
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert rule: {str(e)}")

# Delete alert rule
@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if rule exists and user has access
        rule = await db["alert_rules"].find_one({"_id": ObjectId(rule_id)})
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        if str(rule["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this rule")

        result = await db["alert_rules"].delete_one({"_id": ObjectId(rule_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alert rule not found")

        return {"message": "Alert rule deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert rule: {str(e)}")

# Get all alerts for current user
@router.get("/", response_model=List[AlertOut])
async def get_alerts(
    current_user: dict = Depends(get_current_user),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    days: int = Query(30, description="Number of days of alerts to retrieve")
):
    try:
        user_id = str(current_user["_id"])
        
        # Build query
        query = {"user_id": user_id}
        
        # Add severity filter
        if severity:
            query["severity"] = severity
            
        # Add status filter
        if status:
            query["status"] = status
            
        # Add time filter
        start_date = datetime.utcnow() - timedelta(days=days)
        query["created_at"] = {"$gte": start_date}

        cursor = db["alerts"].find(query).sort("created_at", -1)
        alerts = await cursor.to_list(length=None)

        return [
            AlertOut(
                id=str(alert["_id"]),
                user_id=alert["user_id"],
                title=alert["title"],
                description=alert.get("description"),
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                status=alert["status"],
                source_type=alert["source_type"],
                source_id=alert["source_id"],
                metadata=alert.get("metadata", {}),
                acknowledged_at=alert.get("acknowledged_at"),
                resolved_at=alert.get("resolved_at"),
                created_at=alert["created_at"],
                updated_at=alert["updated_at"]
            )
            for alert in alerts
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

# Acknowledge an alert
@router.put("/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if alert exists and user has access
        alert = await db["alerts"].find_one({"_id": ObjectId(alert_id)})
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if str(alert["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to acknowledge this alert")

        current_time = datetime.utcnow()

        result = await db["alerts"].find_one_and_update(
            {"_id": ObjectId(alert_id)},
            {"$set": {
                "status": "acknowledged",
                "acknowledged_at": current_time,
                "updated_at": current_time
            }},
            return_document=True
        )

        return AlertOut(
            id=str(result["_id"]),
            user_id=result["user_id"],
            title=result["title"],
            description=result.get("description"),
            alert_type=result["alert_type"],
            severity=result["severity"],
            status=result["status"],
            source_type=result["source_type"],
            source_id=result["source_id"],
            metadata=result.get("metadata", {}),
            acknowledged_at=result.get("acknowledged_at"),
            resolved_at=result.get("resolved_at"),
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

# Resolve an alert
@router.put("/{alert_id}/resolve", response_model=AlertOut)
async def resolve_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Check if alert exists and user has access
        alert = await db["alerts"].find_one({"_id": ObjectId(alert_id)})
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if str(alert["user_id"]) != str(current_user["_id"]) and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to resolve this alert")

        current_time = datetime.utcnow()

        result = await db["alerts"].find_one_and_update(
            {"_id": ObjectId(alert_id)},
            {"$set": {
                "status": "resolved",
                "resolved_at": current_time,
                "updated_at": current_time
            }},
            return_document=True
        )

        return AlertOut(
            id=str(result["_id"]),
            user_id=result["user_id"],
            title=result["title"],
            description=result.get("description"),
            alert_type=result["alert_type"],
            severity=result["severity"],
            status=result["status"],
            source_type=result["source_type"],
            source_id=result["source_id"],
            metadata=result.get("metadata", {}),
            acknowledged_at=result.get("acknowledged_at"),
            resolved_at=result.get("resolved_at"),
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

# Get alert summary
@router.get("/summary", response_model=AlertSummary)
async def get_alert_summary(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        # Build aggregation pipeline
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$facet": {
                    "total_alerts": [
                        {"$count": "count"}
                    ],
                    "alerts_by_severity": [
                        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
                    ],
                    "alerts_by_status": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                    ],
                    "alerts_by_type": [
                        {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}}
                    ],
                    "recent_alerts": [
                        {"$sort": {"created_at": -1}},
                        {"$limit": 10}
                    ]
                }
            }
        ]

        # If admin, get all alerts
        if current_user.get("role") == "admin":
            pipeline[0] = {"$match": {}}

        result = await db["alerts"].aggregate(pipeline).to_list(length=None)
        data = result[0] if result else {}

        # Process the results
        total_alerts = data.get("total_alerts", [{}])[0].get("count", 0) if data.get("total_alerts") else 0
        
        alerts_by_severity = {
            item["_id"]: item["count"]
            for item in data.get("alerts_by_severity", [])
        }
        
        alerts_by_status = {
            item["_id"]: item["count"]
            for item in data.get("alerts_by_status", [])
        }
        
        alerts_by_type = {
            item["_id"]: item["count"]
            for item in data.get("alerts_by_type", [])
        }

        recent_alerts = [
            AlertOut(
                id=str(alert["_id"]),
                user_id=alert["user_id"],
                title=alert["title"],
                description=alert.get("description"),
                alert_type=alert["alert_type"],
                severity=alert["severity"],
                status=alert["status"],
                source_type=alert["source_type"],
                source_id=alert["source_id"],
                metadata=alert.get("metadata", {}),
                acknowledged_at=alert.get("acknowledged_at"),
                resolved_at=alert.get("resolved_at"),
                created_at=alert["created_at"],
                updated_at=alert["updated_at"]
            )
            for alert in data.get("recent_alerts", [])
        ]

        return AlertSummary(
            total_alerts=total_alerts,
            alerts_by_severity=alerts_by_severity,
            alerts_by_status=alerts_by_status,
            alerts_by_type=alerts_by_type,
            recent_alerts=recent_alerts
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alert summary: {str(e)}")

# Create a manual alert
@router.post("/manual", response_model=AlertOut)
async def create_manual_alert(
    alert: AlertCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = str(current_user["_id"])
        current_time = datetime.utcnow()

        alert_data = {
            "user_id": user_id,
            "title": alert.title,
            "description": alert.description,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "status": "open",
            "source_type": alert.source_type,
            "source_id": alert.source_id,
            "metadata": alert.metadata or {},
            "created_at": current_time,
            "updated_at": current_time
        }

        result = await db["alerts"].insert_one(alert_data)

        return AlertOut(
            id=str(result.inserted_id),
            **alert_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create manual alert: {str(e)}")

# Get unacknowledged alerts count
@router.get("/unacknowledged-count")
async def get_unacknowledged_count(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        
        query = {
            "user_id": user_id,
            "status": "open"
        }
        
        # If admin, get all unacknowledged alerts
        if current_user.get("role") == "admin":
            query = {"status": "open"}

        count = await db["alerts"].count_documents(query)
        
        return {"unacknowledged_count": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch unacknowledged alerts count: {str(e)}")