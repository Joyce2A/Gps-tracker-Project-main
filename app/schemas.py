## File: app/schemas.py
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models import AssetType, AlertType
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordSchema(BaseModel):
    email: str


class VerifyOTPSchema(BaseModel):
    email: str
    otp: str

class DeviceCreate(BaseModel):
    device_id: str
    device_name: str
    device_model: str
    battery_level: float
    device_status: str

class DeviceOut(BaseModel):
    id: str
    device_id: str
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    battery_level: Optional[float] = None
    device_status: Optional[str] = None
    # time_stamp: Optional[str] = None
    time_stamp: Optional[datetime] = None   


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    battery_level: Optional[float] = None
    device_status: Optional[str] = None

#Assets_schemas

class GeoPoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")
    radius: float = Field(..., ge=0, description="Geofence radius in meters")

#Asset Schemas

class AssetCreate(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    description: Optional[str] = None
    registered_location: GeoPoint

class AssetUpdate(BaseModel):
    asset_name: Optional[str] = None
    asset_type: Optional[str] = None
    description: Optional[str] = None
    registered_location: Optional[GeoPoint] = None

class AssetOut(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    asset_type: str
    description: Optional[str] = None
    registered_location: GeoPoint
    user_id: str
    created_at: datetime
    updated_at: datetime

class AssetDeviceLink(BaseModel):
    asset_id: str
    device_id: str
    status: str
    linked_at: datetime
    linked_by: str
    updated_at: Optional[datetime] = None

class AssetWithDevicesOut(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    asset_type: str
    description: Optional[str] = None
    registered_location: GeoPoint
    user_id: str
    created_at: datetime
    updated_at: datetime
    linked_devices: List[dict]

class LinkedDeviceInfo(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    battery_level: Optional[int] = None
    device_status: Optional[str] = None
    link_status: str
    linked_at: datetime

class AssetDevicesResponse(BaseModel):
    linked_devices: List[LinkedDeviceInfo]

class LinkDeviceRequest(BaseModel):
    asset_id: str
    device_id: str
    status: Optional[str] = "active"

class UpdateLinkStatusRequest(BaseModel):
    asset_id: str
    device_id: str
    status: str

class LinkResponse(BaseModel):
    message: str
    link_id: str

# ========== LOCATION SCHEMAS ==========

class LocationSource(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    NETWORK = "network"
    REGISTERED = "registered"

# class GeoPoint(BaseModel):
#     latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
#     longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")
    
#     @validator('latitude')
#     def validate_latitude(cls, v):
#         if not -90 <= v <= 90:
#             raise ValueError('Latitude must be between -90 and 90')
#         return v
    
#     @validator('longitude')
#     def validate_longitude(cls, v):
#         if not -180 <= v <= 180:
#             raise ValueError('Longitude must be between -180 and 180')
#         return v

class LocationUpdate(BaseModel):
    location: GeoPoint
    source: LocationSource = LocationSource.MANUAL
    accuracy: Optional[float] = Field(None, ge=0, description="Location accuracy in meters")

class LocationOut(BaseModel):
    id: str
    asset_id: Optional[str] = None
    device_id: Optional[str] = None
    location: GeoPoint
    timestamp: datetime
    source: LocationSource
    accuracy: Optional[float]

class AssetLocationHistory(BaseModel):
    id: str
    asset_id: str
    location: GeoPoint
    timestamp: datetime
    source: LocationSource
    accuracy: Optional[float]

class DeviceLocationHistory(BaseModel):
    id: str
    device_id: str
    location: GeoPoint
    timestamp: datetime
    source: LocationSource
    accuracy: Optional[float]

class AssetLocationUpdate(BaseModel):
    asset_id: str
    location: GeoPoint
    source: LocationSource = LocationSource.MANUAL
    accuracy: Optional[float] = None

class DeviceLocationUpdate(BaseModel):
    device_id: str
    location: GeoPoint
    source: LocationSource = LocationSource.MANUAL
    accuracy: Optional[float] = None

class LocationBulkUpdate(BaseModel):
    assets: List[AssetLocationUpdate] = []
    devices: List[DeviceLocationUpdate] = []

# ========== ALERT SCHEMAS ==========

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class AlertConditionType(str, Enum):
    BATTERY_LEVEL = "battery_level"
    DEVICE_STATUS = "device_status"
    GEO_FENCE = "geo_fence"
    OFFLINE_DURATION = "offline_duration"
    MOVEMENT_DETECTED = "movement_detected"

class AlertCondition(BaseModel):
    condition_type: AlertConditionType
    threshold: Optional[float] = None
    operator: Optional[str] = Field(None, description="Comparison operator: <, >, <=, >=, =, !=")
    value: Optional[Any] = None
    duration_minutes: Optional[int] = Field(None, description="Duration condition must be true")
    geo_fence_id: Optional[str] = None

class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    alert_type: AlertType
    conditions: AlertCondition
    is_active: bool = True
    severity: AlertSeverity = AlertSeverity.MEDIUM
    notification_channels: List[str] = Field(default=["email"])

class AlertRuleOut(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    alert_type: AlertType
    conditions: Dict[str, Any]
    is_active: bool
    severity: AlertSeverity
    notification_channels: List[str]
    created_at: datetime
    updated_at: datetime

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    alert_type: Optional[AlertType] = None
    conditions: Optional[AlertCondition] = None
    is_active: Optional[bool] = None
    severity: Optional[AlertSeverity] = None
    notification_channels: Optional[List[str]] = None

class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    alert_type: AlertType
    severity: AlertSeverity
    source_type: str = Field(..., description="asset, device, or system")
    source_id: str = Field(..., description="ID of the asset, device, or system")
    metadata: Optional[Dict[str, Any]] = None

class AlertOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    source_type: str
    source_id: str
    metadata: Dict[str, Any]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None

class AlertSummary(BaseModel):
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    alerts_by_type: Dict[str, int]
    recent_alerts: List[AlertOut]

# ========== DASHBOARD SCHEMAS ==========

class DashboardStats(BaseModel):
    total_assets: int
    total_devices: int
    total_alerts: int
    open_alerts: int
    linked_devices_count: int
    assets_by_type: Dict[str, int]
    devices_by_status: Dict[str, int]
    alerts_by_severity: Dict[str, int]

class AssetStatusSummary(BaseModel):
    total_assets: int
    assets_with_devices: int
    assets_without_devices: int
    assets_online: int
    assets_offline: int
    assets_by_type: Dict[str, int]

class DeviceStatusSummary(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    maintenance_devices: int
    error_devices: int
    devices_by_model: Dict[str, int]
    average_battery_level: Optional[float]

class RecentActivity(BaseModel):
    id: str
    type: str = Field(..., description="asset_created, device_linked, alert_triggered, etc.")
    description: str
    source_id: str
    timestamp: datetime
    user_id: Optional[str]

class DashboardOverview(BaseModel):
    stats: DashboardStats
    asset_summary: AssetStatusSummary
    device_summary: DeviceStatusSummary
    recent_activities: List[RecentActivity]
    recent_alerts: List[AlertOut]

# ========== ALERT SCHEMAS ==========

class AlertConditionType(str, Enum):
    BATTERY_LEVEL = "battery_level"
    DEVICE_STATUS = "device_status"
    GEO_FENCE = "geo_fence"
    OFFLINE_DURATION = "offline_duration"
    CUSTOM = "custom"

class AlertCondition(BaseModel):
    condition_type: AlertConditionType
    threshold: Optional[float] = None
    operator: Optional[str] = Field(None, description="Comparison operator: <, >, <=, >=, =, !=")
    value: Optional[Any] = None
    duration_minutes: Optional[int] = Field(None, description="Duration condition must be true")
    geo_fence_id: Optional[str] = None

class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    alert_type: AlertType
    conditions: AlertCondition
    is_active: bool = True
    severity: AlertSeverity = AlertSeverity.MEDIUM
    notification_channels: List[str] = Field(default=["email"])

class AlertRuleOut(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    alert_type: AlertType
    conditions: Dict[str, Any]
    is_active: bool
    severity: AlertSeverity
    notification_channels: List[str]
    created_at: datetime
    updated_at: datetime

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    alert_type: Optional[AlertType] = None
    conditions: Optional[AlertCondition] = None
    is_active: Optional[bool] = None
    severity: Optional[AlertSeverity] = None
    notification_channels: Optional[List[str]] = None

class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    alert_type: AlertType
    severity: AlertSeverity
    source_type: str = Field(..., description="asset, device, or system")
    source_id: str = Field(..., description="ID of the asset, device, or system")
    metadata: Optional[Dict[str, Any]] = None

class AlertOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    source_type: str
    source_id: str
    metadata: Dict[str, Any]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    description: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None

class AlertSummary(BaseModel):
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    alerts_by_type: Dict[str, int]
    recent_alerts: List[AlertOut]

# ========== DASHBOARD SCHEMAS ==========

class DashboardStats(BaseModel):
    total_assets: int
    total_devices: int
    total_alerts: int
    open_alerts: int
    linked_devices_count: int
    assets_by_type: Dict[str, int]
    devices_by_status: Dict[str, int]
    alerts_by_severity: Dict[str, int]

class AssetStatusSummary(BaseModel):
    total_assets: int
    assets_with_devices: int
    assets_without_devices: int
    assets_online: int
    assets_offline: int
    assets_by_type: Dict[str, int]

class DeviceStatusSummary(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    maintenance_devices: int
    error_devices: int
    devices_by_model: Dict[str, int]
    average_battery_level: Optional[float]

class RecentActivity(BaseModel):
    id: str
    type: str = Field(..., description="asset_created, device_linked, alert_triggered, etc.")
    description: str
    source_id: str
    timestamp: datetime
    user_id: Optional[str]

class DashboardOverview(BaseModel):
    stats: DashboardStats
    asset_summary: AssetStatusSummary
    device_summary: DeviceStatusSummary
    recent_activities: List[RecentActivity]
    recent_alerts: List[AlertOut]

# # class LocationIn(BaseModel):
# #     device_id: str = Field(..., description="Unique device ID linked to this location")
# #     latitude: float = Field(..., description="Latitude in decimal degrees")
# #     longitude: float = Field(..., description="Longitude in decimal degrees")
# #     timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Time of location capture")
# class LocationIn(BaseModel):
#     device_id: str = Field(..., description="Unique ID of the device sending location")
#     latitude: float = Field(..., description="Latitude in decimal degrees")
#     longitude: float = Field(..., description="Longitude in decimal degrees")
#     timestamp: Optional[datetime] = Field(
#         default_factory=datetime.utcnow, description="Timestamp of location capture"
#     )


# class LocationOut(BaseModel):
#     id: str
#     device_id: str
#     latitude: float
#     longitude: float
#     timestamp: datetime
#     distance_moved: float
#     movement_status: str
#     alert_message: Optional[str] = None


# class AlertOut(BaseModel):
#     id: Optional[str]
#     tracker_id: str
#     alert_type: str
#     distance_m: float
#     threshold_m: float
#     message: str
#     timestamp: datetime



# class AlertOut(BaseModel):
#     id: str
#     device_id: str
#     timestamp: datetime
#     alert_type: str
#     message: str
#     metadata: Dict[str, Any]




# class AlertRuleCreate(BaseModel):
#     name: str
#     type: str
#     params: Dict[str, Any]

