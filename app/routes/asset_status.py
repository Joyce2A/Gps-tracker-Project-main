from fastapi import APIRouter
from app.database import db

# router = APIRouter(prefix="/assets", tags=["Asset Live Status"])
router = APIRouter()


# @router.get("/live-status")
# async def get_live_asset_status():
#     pipeline = [
#         {
#             "$lookup": {
#                 "from": "assets",
#                 "localField": "asset_id",
#                 "foreignField": "asset_id",
#                 "as": "asset"
#             }
#         },
#         {"$unwind": "$asset"}
#     ]

#     data = await db.asset_status.aggregate(pipeline).to_list(None)

#     return [
#         {
#             "asset_id": d["asset_id"],
#             "asset_name": d["asset"]["asset_name"],
#             "lat": d["last_lat"],
#             "lon": d["last_lon"],
#             "inside_geofence": d["inside_geofence"],
#             "distance": round(d["distance_from_base"], 2),
#             "device_id": d["device_id"],
#             "updated_at": d["updated_at"]
#         }
#         for d in data
#     ]


@router.get("/live-status")
async def live_status():
    cursor = db.asset_status.find({})
    results = []

    async for doc in cursor:
        results.append({
            "asset_id": doc["asset_id"],
            "device_id": doc["device_id"],

            # Asset location
            "lat": doc["last_lat"],
            "lon": doc["last_lon"],

            # 🔴 REQUIRED for map correctness
            "geofence_lat": doc.get("geofence_lat"),
            "geofence_lon": doc.get("geofence_lon"),
            "geofence_radius": doc.get("geofence_radius"),

            # meters
            "distance": doc["distance_from_base"],
            "inside_geofence": doc["inside_geofence"],

            "updated_at": doc["updated_at"],
        })

    return results