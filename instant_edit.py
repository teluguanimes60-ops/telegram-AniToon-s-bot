# ==========================================
# AniToon Bot - Instant Caption Editor
# ==========================================

from jobs import update_job

# Stores message IDs that can be edited later
EDIT_CACHE = {}


def save_editable_message(user_id, message):
    """
    Save the sent media message for later caption editing.
    """
    EDIT_CACHE[user_id] = {
        "chat_id": message.chat.id,
        "message_id": message.id,
    }


def get_editable_message(user_id):
    """
    Get saved message info.
    """
    return EDIT_CACHE.get(user_id)


async def instant_edit_caption(client, user_id, new_caption):
    """
    Instantly edit the caption of the last uploaded media.
    """

    data = get_editable_message(user_id)

    if not data:
        return False

    try:
        await client.edit_message_caption(
            chat_id=data["chat_id"],
            message_id=data["message_id"],
            caption=new_caption
        )

        update_job(str(data["message_id"]), "caption", new_caption)

        return True

    except Exception as e:
        print("Instant Edit Error:", e)
        return False
