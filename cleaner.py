# ==========================================================
# 🤖 AniToon Bot - Cleaner System (Production v8)
# ==========================================================

from typing import Dict

LAST_BOT_MESSAGES: Dict[int, object] = {}
LAST_USER_MESSAGES: Dict[int, object] = {}

# ==========================================================
# DELETE LAST BOT MESSAGE
# ==========================================================

async def delete_last_bot(user_id: int):
    msg = LAST_BOT_MESSAGES.pop(user_id, None)

    if msg:
        try:
            await msg.delete()
        except Exception:
            pass


# ==========================================================
# DELETE LAST USER MESSAGE
# ==========================================================

async def delete_last_user(user_id: int):
    msg = LAST_USER_MESSAGES.pop(user_id, None)

    if msg:
        try:
            await msg.delete()
        except Exception:
            pass


# ==========================================================
# CLEAN CHAT
# ==========================================================

async def clean_chat(user_id: int):
    await delete_last_bot(user_id)
    await delete_last_user(user_id)


# ==========================================================
# SEND CLEAN MESSAGE
# ==========================================================

async def send_clean(
    message,
    text,
    reply_markup=None,
    disable_web_page_preview=True
):
    user_id = message.from_user.id

    await clean_chat(user_id)

    sent = await message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=disable_web_page_preview
    )

    LAST_USER_MESSAGES[user_id] = message
    LAST_BOT_MESSAGES[user_id] = sent

    return sent


# ==========================================================
# REPLACE BOT MESSAGE
# ==========================================================

async def replace_bot_message(
    message,
    text,
    reply_markup=None,
    disable_web_page_preview=True
):
    user_id = message.from_user.id

    await delete_last_bot(user_id)

    sent = await message.reply_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=disable_web_page_preview
    )

    LAST_BOT_MESSAGES[user_id] = sent

    return sent


# ==========================================================
# SAVE USER MESSAGE
# ==========================================================

async def save_user_message(user_id, message):
    LAST_USER_MESSAGES[user_id] = message


# ==========================================================
# SAVE BOT MESSAGE
# ==========================================================

async def save_bot_message(user_id, message):
    LAST_BOT_MESSAGES[user_id] = message


# ==========================================================
# COMPATIBILITY
# ==========================================================

async def remember_user(message):
    LAST_USER_MESSAGES[message.from_user.id] = message


async def remember_bot(message):
    LAST_BOT_MESSAGES[message.chat.id] = message


# ==========================================================
# RESET USER
# ==========================================================

def reset_user(user_id):
    LAST_USER_MESSAGES.pop(user_id, None)
    LAST_BOT_MESSAGES.pop(user_id, None)


# ==========================================================
# RESET ALL
# ==========================================================

def reset_all():
    LAST_USER_MESSAGES.clear()
    LAST_BOT_MESSAGES.clear()
