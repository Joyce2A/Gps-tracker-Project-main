from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId

async def check_devices():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.gps_tracker_db
    
    # Get all devices
    devices = await db["devices"].find().to_list(length=None)
    print(f"Total devices in database: {len(devices)}")
    
    for device in devices:
        print(f"\nDevice ID: {device['_id']}")
        print(f"User ID: {device['user_id']}")
        print(f"Device details: {device}")

if __name__ == "__main__":
    asyncio.run(check_devices())