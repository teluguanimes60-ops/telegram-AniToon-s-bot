# ==========================================
# AniToon Bot - CLEANER SYSTEM (FIXED)
# ==========================================

# store last messages per user
last_bot_message = {}
last_user_message = {}


# =========================
# SAVE BOT MESSAGE
# =========================
async def save_bot_message(user_id, message):
    """
    Save latest bot message for cleanup
    """
    last_bot_message[user_id] = message


# =========================
# SAVE USER MESSAGE
# =========================
async def save_user_message(user_id, message):
    """
    Save latest user message for cleanup
    """
    last_user_message[user_id] = message


# =========================
# DELETE LAST BOT MESSAGE
# =========================
async def delete_last_bot(user_id):
    """
    Delete previous bot message
    """
    msg = last_bot_message.get(user_id)

    if msg:
        try:
            await msg.delete()
        except:
            pass

        last_bot_message.pop(user_id, None)


# =========================
# DELETE LAST USER MESSAGE
# =========================
async def delete_last_user(user_id):
    """
    Delete previous user message
    """
    msg = last_user_message.get(user_id)

    if msg:
        try:
            await msg.delete()
        except:
            pass

        last_user_message.pop(user_id, None)


# =========================
# CLEAN FULL CHAT
# =========================
async def clean_chat(user_id):
    """
    Delete both bot + user last messages
    """
    await delete_last_bot(user_id)
    await delete_last_user(user_id)


# =========================
# SEND CLEAN MESSAGE
# =========================
async def send_clean(message, text, reply_markup=None):
    """
    Deletes old messages and sends a new clean message
    """

    uid = message.from_user.id

    await clean_chat(uid)

    m = await message.reply_text(
        text,
        reply_markup=reply_markup
    )

    await save_bot_message(uid, m)
    await save_user_message(uid, message)

    return m
