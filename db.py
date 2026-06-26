# ==========================================
# AniToon Bot - MONGO DB CORE (GOD V4)
# ==========================================

import os
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------- MONGO CONFIG ----------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI not found in environment variables")

client = AsyncIOMotorClient(MONGO_URI)

db = client["AniToonBot"]

# collections
users_col = db["users"]
thumb_col = db["thumbnails"]
settings_col = db["settings"]

# ==========================================
# 👤 USER SYSTEM
# ==========================================

async def add_user(user_id: int, name: str = None):

    await users_col.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "name": name,
                "created_at": _now()
            },
            "$set": {
                "last_seen": _now()
            }
        },
        upsert=True
    )

async def get_user(user_id: int):
    return await users_col.find_one({"_id": user_id})

async def update_user(user_id: int, data: dict):

    await users_col.update_one(
        {"_id": user_id},
        {"$set": data},
        upsert=True
    )

# ==========================================
# 🖼 THUMBNAIL SYSTEM (PERMANENT)
# ==========================================

async def save_thumbnail(user_id: int, file_id: str):

    await thumb_col.update_one(
        {"_id": user_id},
        {
            "$set": {
                "file_id": file_id,
                "updated_at": _now()
            }
        },
        upsert=True
    )

async def get_thumbnail(user_id: int):

    data = await thumb_col.find_one({"_id": user_id})

    if data:
        return data.get("file_id")

    return None

# ==========================================
# ⚙️ SETTINGS SYSTEM
# ==========================================

async def set_setting(user_id: int, key: str, value):

    await settings_col.update_one(
        {"_id": user_id},
        {"$set": {key: value}},
        upsert=True
    )

async def get_setting(user_id: int, key: str):

    data = await settings_col.find_one({"_id": user_id})

    if data:
        return data.get(key)

    return None

# ==========================================
# ⏱ TIME HELP
# ==========================================

import time

def _now():
    return int(time.time())
