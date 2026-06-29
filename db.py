# ==========================================================
# 🤖 AniToon Bot - Database Manager (Production v5)
# ==========================================================

import os
import time

from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================================
# MONGODB
# ==========================================================

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not found.")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=30000,
    tls=True
)

db = client["AniToonBot"]

users = db["users"]
thumbs = db["thumbnails"]
settings = db["settings"]
bot_settings = db["bot_settings"]
stats = db["stats"]

# ==========================================================
# TIME
# ==========================================================

def now():
    return int(time.time())

# ==========================================================
# USER SYSTEM
# ==========================================================

async def add_user(user_id: int, name: str = ""):

    await users.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "name": name,
                "joined": now()
            },
            "$set": {
                "last_seen": now()
            }
        },
        upsert=True
    )


async def get_user(user_id: int):

    return await users.find_one({"_id": user_id})


async def update_user(user_id: int, data: dict):

    await users.update_one(
        {"_id": user_id},
        {"$set": data},
        upsert=True
    )


async def total_users():

    return await users.count_documents({})

# ==========================================================
# THUMBNAILS
# ==========================================================

async def save_thumbnail(user_id: int, file_id: str):

    await thumbs.update_one(
        {"_id": user_id},
        {
            "$set": {
                "file_id": file_id,
                "updated": now()
            }
        },
        upsert=True
    )


async def get_thumbnail(user_id: int):

    data = await thumbs.find_one({"_id": user_id})

    if data:
        return data.get("file_id")

    return None


async def delete_thumbnail(user_id: int):

    await thumbs.delete_one({"_id": user_id})

# ==========================================================
# USER SETTINGS
# ==========================================================

DEFAULT_SETTINGS = {
    "thumbnail": "auto",
    "cleaner": True,
    "show_media_info": True
}


async def get_settings(user_id: int):

    data = await settings.find_one({"_id": user_id})

    if not data:

        await settings.insert_one({
            "_id": user_id,
            **DEFAULT_SETTINGS
        })

        return DEFAULT_SETTINGS.copy()

    result = DEFAULT_SETTINGS.copy()
    result.update(data)

    return result


async def get_setting(user_id: int, key: str):

    data = await get_settings(user_id)

    return data.get(key)


async def set_setting(user_id: int, key: str, value):

    await settings.update_one(
        {"_id": user_id},
        {"$set": {key: value}},
        upsert=True
    )

# ==========================================================
# OWNER BOT SETTINGS
# ==========================================================

BOT_DEFAULTS = {
    "_id": "config",
    "queue_limit": 20,
    "cleaner": True,
    "auto_thumb": True,
    "maintenance": False
}


async def load_bot_settings():

    data = await bot_settings.find_one({"_id": "config"})

    if not data:

        await bot_settings.insert_one(BOT_DEFAULTS)

        return BOT_DEFAULTS.copy()

    result = BOT_DEFAULTS.copy()
    result.update(data)

    return result


async def get_bot_setting(key):

    data = await load_bot_settings()

    return data.get(key)


async def set_bot_setting(key, value):

    await bot_settings.update_one(
        {"_id": "config"},
        {"$set": {key: value}},
        upsert=True
    )

# ==========================================================
# BOT STATISTICS
# ==========================================================

async def increase_stat(name):

    await stats.update_one(
        {"_id": "stats"},
        {"$inc": {name: 1}},
        upsert=True
    )


async def get_stats():

    data = await stats.find_one({"_id": "stats"})

    if not data:
        return {}

    return data

# ==========================================================
# DATABASE INIT
# ==========================================================

async def init_database():

    await client.admin.command("ping")

    await users.create_index("last_seen")
    await thumbs.create_index("updated")

    await load_bot_settings()

    print("✅ MongoDB Connected Successfully")
