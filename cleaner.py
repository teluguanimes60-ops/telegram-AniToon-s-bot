# ==========================================================
# 🤖 AniToon Bot - Cleaner System (Project V5)
# ==========================================================

from typing import Dict

# ==========================================================
# STORAGE
# ==========================================================

LAST_BOT_MESSAGES: Dict[int, object] = {}
LAST_USER_MESSAGES: Dict[int, object] = {}


# ==========================================================
# SAVE BOT MESSAGE
# ==========================================================

async def save_bot_message(user_id: int, message):

    LAST_BOT_MESSAGES[user_id] = message


# ==========================================================
# SAVE USER MESSAGE
# ==========================================================

async def save_user_message(user_id: int, message):

    LAST_USER_MESSAGES[user_id] = message


# ==========================================================
# DELETE BOT MESSAGE
# ==========================================================

async def delete_bot_message(user_id: int):

    msg = LAST_BOT_MESSAGES.pop(user_id, None)

    if not msg:
        return

    try:
        await msg.delete()
    except Exception:
        pass


# ==========================================================
# DELETE USER MESSAGE
# ==========================================================

async def delete_user_message(user_id: int):

    msg = LAST_USER_MESSAGES.pop(user_id, None)

    if not msg:
        return

    try:
        await msg.delete()
    except Exception:
        pass


# ==========================================================
# CLEAN CHAT
# ==========================================================

async def clean_chat(user_id: int):

    await delete_bot_message(user_id)
    await delete_user_message(user_id)


# ==========================================================
# SEND CLEAN MESSAGE
# ==========================================================

async def send_clean(
    message,
    text,
    reply_markup=None,
    disable_web_page_preview=True
):
    """
    Delete previous bot/user messages,
    send a fresh message,
    and remember it for next cleanup.
    """

    user_id = message.from_user.id

    await clean_chat(user_id)

    sent = await message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=disable_web_page_preview
    )

    await save_user_message(user_id, message)
    await save_bot_message(user_id, sent)

    return sent


# ==========================================================
# REMOVE ONLY BOT MESSAGE
# ==========================================================

async def replace_bot_message(
    message,
    text,
    reply_markup=None
):
    """
    Delete only the previous bot message.
    Keep the user's message.
    Useful for menus.
    """

    user_id = message.from_user.id

    await delete_bot_message(user_id)

    sent = await message.reply_text(
        text=text,
        reply_markup=reply_markup
    )

    await save_bot_message(user_id, sent)

    return sent


# ==========================================================
# RESET USER CACHE
# ==========================================================

def reset_user(user_id: int):

    LAST_BOT_MESSAGES.pop(user_id, None)
    LAST_USER_MESSAGES.pop(user_id, None)


# ==========================================================
# RESET ALL
# ==========================================================

def reset_all():

    LAST_BOT_MESSAGES.clear()
    LAST_USER_MESSAGES.clear()
