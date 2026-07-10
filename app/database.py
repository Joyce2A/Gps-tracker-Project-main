import motor.motor_asyncio
import logging
from app.config import settings
from typing import Optional, Dict

logger = logging.getLogger(__name__)

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def init_db():
    """Initialize database indexes"""
    try:
        await db["devices"].create_index("device_id", unique=True)
        await db["locations"].create_index([("device_id", 1), ("timestamp", -1)])
        await db["alerts"].create_index("device_id")
        await db["users"].create_index("email", unique=True)
        logger.info("DB indexes ensured")
    except Exception:
        logger.exception("Error creating indexes")

async def get_user_by_email(email: str) -> Optional[Dict]:
    """Find a user by email in the users collection"""
    return await db["users"].find_one({"email": email})

async def create_user(user_data: Dict) -> Optional[str]:
    """Create a new user in the users collection"""
    try:
        result = await db["users"].insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


