# ==========================================================
# 🤖 AniToon's Bot - Instant Edit System
# ==========================================================

import time

# ----------------------------------------------------------
# Stores the last uploaded media message for each user
# ----------------------------------------------------------

EDIT_CACHE = {}

CACHE_EXPIRE = 60 * 60   # 1 hour


# ----------------------------------------------------------
# Save uploaded media
# ----------------------------------------------------------

def save_editable_message(user_id, message):

    EDIT_CACHE[user_id] = {
        "chat_id": message.chat.id,
        "message_id": message.id,
        "time": time.time()
    }


# ----------------------------------------------------------
# Get uploaded media
# ----------------------------------------------------------

def get_editable_message(user_id):

    data = EDIT_CACHE.get(user_id)

    if not data:
        return None

    if time.time() - data["time"] > CACHE_EXPIRE:

        EDIT_CACHE.pop(user_id, None)
        return None

    return data


# ----------------------------------------------------------
# Remove cache
# ----------------------------------------------------------

def clear_editable_message(user_id):

    EDIT_CACHE.pop(user_id, None)


# ----------------------------------------------------------
# Instant Caption Edit
# ----------------------------------------------------------

async def instant_edit_caption(client, user_id, new_caption):

    data = get_editable_message(user_id)

    if data is None:
        return False, "❌ No recently uploaded file found."

    try:

        caption = (new_caption or "").strip()

        if len(caption) > 1024:
            caption = caption[:1024]

        await client.edit_message_caption(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            caption=caption
        )

        return True, "✅ Caption updated."

    except Exception as e:

        print("Instant Edit Error:", e)
        return False, "❌ Unable to edit caption."
