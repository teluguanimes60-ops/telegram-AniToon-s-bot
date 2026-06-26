# ==========================================
# AniToon Bot V2 - Cleaner
# ==========================================

# Stores the last bot message for each user
last_bot_message = {}

# Stores the last user message for each user
last_user_message = {}


async def save_bot_message(user_id, message):
    """
    Save the latest bot message.
    """
    last_bot_message[user_id] = message


async def save_user_message(user_id, message):
    """
    Save the latest user message.
    """
    last_user_message[user_id] = message


async def delete_last_bot(user_id):
    """
    Delete the previous bot message.
    """
    msg = last_bot_message.get(user_id)

    if msg:
        try:
            await msg.delete()
        except:
            pass

        last_bot_message.pop(user_id, None)


async def delete_last_user(user_id):
    """
    Delete the previous user message.
    """
    msg = last_user_message.get(user_id)

    if msg:
        try:
            await msg.delete()
        except:
            pass

        last_user_message.pop(user_id, None)


async def clean_chat(user_id):
    """
    Delete both previous bot and user messages.
    """
    await delete_last_bot(user_id)
    await delete_last_user(user_id)


async def send_clean(message, text, reply_markup=None):
    """
    Delete old messages and send a new bot message.
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
