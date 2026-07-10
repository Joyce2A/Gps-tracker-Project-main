# app/models/__init__.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TRACKING_VIEW = "tracking_view"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class AssetType(str, Enum):
    VEHICLE = "vehicle"
    EQUIPMENT = "equipment"
    CONTAINER = "container"
    PERSONNEL = "personnel"
    OTHER = "other"

class AlertType(str, Enum):
    GEO_FENCE = "geo_fence"
    BATTERY_LOW = "battery_low"
    DEVICE_OFFLINE = "device_offline"
    MOVEMENT_DETECTED = "movement_detected"

# Additional enums for the new functionality
class LocationSource(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    NETWORK = "network"
    REGISTERED = "registered"

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

class LinkStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
