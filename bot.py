# ==========================================================
# 🤖 AniToon's Bot Platform
# bot.py (Part 1)
# ==========================================================

import os
import time
import asyncio
import threading
import uuid

from flask import Flask

from pyrogram import Client, filters, idle
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# =======================
# Project Imports
# =======================

from buttons import (
    start_buttons,
    help_buttons,
    rename_buttons,
    thumb_buttons,
    download_buttons,
    upload_buttons
)

from help_text import HELP_TEXT

from jobs import (
    create_job,
    get_job,
    update_job,
    delete_job
)

from queue_system import (
    start_queue,
    add_to_queue,
    is_full,
    active_count
)

from engine import process_pipeline

from instant_edit import (
    instant_edit_caption,
    save_editable_message
)

from thumbnail import (
    save_thumb
)

# =======================
# Environment
# =======================

API_ID = int(os.getenv("API_ID"))

API_HASH = os.getenv("API_HASH")

BOT_TOKEN = os.getenv("BOT_TOKEN")

PORT = int(os.getenv("PORT", 10000))

# =======================
# Flask (Render Keep Alive)
# =======================

web = Flask(__name__)

@web.route("/")
def home():
    return "🚀 AniToon's Bot Platform Online"

# =======================
# Pyrogram Client
# =======================

bot = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=20
)

# =======================
# Runtime Storage
# =======================

# Waiting for rename text
WAITING_RENAME = {}

# Waiting for instant edit caption
WAITING_EDIT = {}

# Waiting for thumbnail upload
WAITING_THUMB = {}

# User -> Current Job
USER_JOB = {}

# User -> Last Bot Message
LAST_BOT_MESSAGE = {}

# User -> Last User Message
LAST_USER_MESSAGE = {}

# =======================
# Helper Functions
# =======================

def new_job_id():

    return str(uuid.uuid4())


async def delete_old_messages(user_id):

    """
    Placeholder.

    Will be completed in Part 2.
    """

    return


# ==========================================================
# End of Part 1
# ==========================================================

# ==========================================================
# 🤖 MESSAGE CLEANER
# ==========================================================

async def delete_old_messages(user_id):

    try:

        if user_id in LAST_BOT_MESSAGE:

            chat_id, msg_id = LAST_BOT_MESSAGE[user_id]

            await bot.delete_messages(
                chat_id,
                msg_id
            )

    except:
        pass

    try:

        if user_id in LAST_USER_MESSAGE:

            chat_id, msg_id = LAST_USER_MESSAGE[user_id]

            await bot.delete_messages(
                chat_id,
                msg_id
            )

    except:
        pass


# ==========================================================
# /START
# ==========================================================

@bot.on_message(filters.command("start"))

async def start_handler(client, message):

    uid = message.from_user.id

    LAST_USER_MESSAGE[uid] = (
        message.chat.id,
        message.id
    )

    await delete_old_messages(uid)

    text = f"""
🎉 **Welcome to AniToon's File Bot**

━━━━━━━━━━━━━━━━━━

🎬 Rename Videos

📂 Rename Documents

🔄 Convert Videos

⚡ Instant Caption Edit

🖼 Custom Thumbnail

🤖 Auto Thumbnail

🚫 Without Thumbnail

📊 Progress Bar

━━━━━━━━━━━━━━━━━━

👥 Active Users : **{active_count()}/20**

📤 Send me a Video or File to begin.
"""

    m = await message.reply_text(
        text,
        reply_markup=start_buttons()
    )

    LAST_BOT_MESSAGE[uid] = (
        m.chat.id,
        m.id
    )


# ==========================================================
# /HELP
# ==========================================================

@bot.on_message(filters.command("help"))

async def help_handler(client, message):

    uid = message.from_user.id

    LAST_USER_MESSAGE[uid] = (
        message.chat.id,
        message.id
    )

    await delete_old_messages(uid)

    m = await message.reply_text(
        HELP_TEXT,
        reply_markup=help_buttons()
    )

    LAST_BOT_MESSAGE[uid] = (
        m.chat.id,
        m.id
    )


# ==========================================================
# HELP BUTTON
# ==========================================================

@bot.on_callback_query(filters.regex("^help$"))

async def help_callback(client, query):

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=help_buttons()
    )


# ==========================================================
# BACK BUTTON
# ==========================================================

@bot.on_callback_query(filters.regex("^home$"))

async def home_callback(client, query):

    text = f"""
🎉 **Welcome to AniToon's File Bot**

━━━━━━━━━━━━━━━━━━

🎬 Rename Videos

📂 Rename Documents

🔄 Convert Videos

⚡ Instant Caption Edit

🖼 Custom Thumbnail

🤖 Auto Thumbnail

🚫 Without Thumbnail

━━━━━━━━━━━━━━━━━━

👥 Active Users : **{active_count()}/20**

📤 Send a file to start.
"""

    await query.message.edit_text(
        text,
        reply_markup=start_buttons()
    )

