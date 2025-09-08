from motor.motor_asyncio import AsyncIOMotorClient
from plugins.config import Config

client = AsyncIOMotorClient(Config.DATABASE_URL)
db = client["uploadbot"]
banned_collection = db["banned_users"]

async def ban_user(user_id: int):
    await banned_collection.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def unban_user(user_id: int):
    await banned_collection.delete_one({"user_id": user_id})

async def is_banned(user_id: int):
    user = await banned_collection.find_one({"user_id": user_id})
    return bool(user)
