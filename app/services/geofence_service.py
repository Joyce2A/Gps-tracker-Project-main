# app/services/geofence_service.py

import math
from typing import Dict


# --------------------------------------------------
# DISTANCE CALCULATION (HAVERSINE FORMULA)
# --------------------------------------------------
def calculate_distance_meters(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance in meters between two GPS coordinates
    using the Haversine formula.
    """

    EARTH_RADIUS_METERS = 6371000  # Earth radius

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_METERS * c


# --------------------------------------------------
# GEOFENCE CHECK
# --------------------------------------------------
def check_geofence(
    device_lat: float,
    device_lon: float,
    base_lat: float,
    base_lon: float,
    radius_meters: float
) -> Dict[str, float | bool]:
    """
    Check whether a device is inside or outside the geofence.

    Base location = factory / yard / registered location

    Returns:
    {
        "inside": bool,
        "distance_meters": float,
        "radius_meters": float
    }
    """

    distance = calculate_distance_meters(
        base_lat,
        base_lon,
        device_lat,
        device_lon
    )

    return {
        "inside": distance <= radius_meters,
        "distance_meters": round(distance, 2),
        "radius_meters": radius_meters
    }
