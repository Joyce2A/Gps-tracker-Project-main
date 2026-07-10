import asyncio
import logging
from datetime import datetime, timedelta
from app.database import db

logger = logging.getLogger("DeviceStatusChecker")

CHECK_INTERVAL = 60          # every 1 minute
OFFLINE_THRESHOLD = 5        # minutes


async def device_offline_checker():
    while True:
        try:
            threshold_time = datetime.utcnow() - timedelta(minutes=OFFLINE_THRESHOLD)

            result = await db.devices.update_many(
                {
                    "last_seen": {"$lt": threshold_time},
                    "device_status": "online"
                },
                {
                    "$set": {
                        "device_status": "offline",
                        "offline_since": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                logger.info(f"🔴 Marked {result.modified_count} devices as OFFLINE")

        except Exception:
            logger.exception("❌ Error in offline checker")

        await asyncio.sleep(CHECK_INTERVAL)

