# ==========================================================
# 🤖 AniToon Bot - Instant Edit Engine (Project V5)
# ==========================================================

import time

# ==========================================================
# CACHE
# ==========================================================

EDIT_CACHE = {}

CACHE_EXPIRE = 60 * 60 * 24   # 24 Hours


# ==========================================================
# SAVE MESSAGE
# ==========================================================

def save_editable_message(user_id: int, message):

    EDIT_CACHE[user_id] = {
        "chat_id": message.chat.id,
        "message_id": message.id,
        "date": time.time()
    }


# ==========================================================
# GET MESSAGE
# ==========================================================

def get_editable_message(user_id: int):

    data = EDIT_CACHE.get(user_id)

    if not data:
        return None

    if time.time() - data["date"] > CACHE_EXPIRE:
        EDIT_CACHE.pop(user_id, None)
        return None

    return data


# ==========================================================
# REMOVE CACHE
# ==========================================================

def clear_editable_message(user_id: int):

    EDIT_CACHE.pop(user_id, None)


# ==========================================================
# CHECK
# ==========================================================

def has_editable_message(user_id: int):

    return get_editable_message(user_id) is not None


# ==========================================================
# INSTANT EDIT
# ==========================================================

async def instant_edit_caption(
    client,
    user_id: int,
    new_caption: str
):

    data = get_editable_message(user_id)

    if data is None:
        return False, "❌ No editable file found."

    try:

        caption = (new_caption or "").strip()

        if len(caption) > 1024:
            caption = caption[:1024]

        await client.edit_message_caption(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            caption=caption
        )

        return True, "✅ File renamed instantly."

    except Exception as e:

        print("Instant Edit:", e)

        return False, "❌ Telegram doesn't allow editing this file anymore."


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_cache():

    now = time.time()

    expired = []

    for uid, data in EDIT_CACHE.items():

        if now - data["date"] > CACHE_EXPIRE:
            expired.append(uid)

    for uid in expired:
        EDIT_CACHE.pop(uid, None)

    return len(expired)
