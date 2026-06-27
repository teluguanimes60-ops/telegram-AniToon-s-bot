# ==========================================================
# 🤖 AniToon Bot
# Main Bot (Part 1/5)
# ==========================================================

import os
import asyncio
import threading

from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from buttons import (
    start_buttons,
    settings_buttons,
    about_buttons,
    help_buttons,
    file_buttons,
    convert_buttons,
    thumbnail_buttons
)

from help_text import HELP_TEXT

from cleaner import send_clean

from db import (
    add_user
)

from jobs import (
    create_job,
    get_job,
    update_job,
    delete_job
)

from queue_system import (
    add_to_queue,
    user_processing,
    queue_size,
    active_count
)

from states import (
    set_state,
    get_state,
    clear_state
)

from engine import process_pipeline

# ==========================================================
# ENVIRONMENT
# ==========================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

PORT = int(os.environ.get("PORT", "10000"))

CHANNEL_POST = "https://t.me/Anitoon_edit/33"

# ==========================================================
# FLASK
# ==========================================================

app = Flask(__name__)

@app.route("/")
def home():
    return "AniToon Bot Running ✅"

# ==========================================================
# PYROGRAM
# ==========================================================

bot = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================================
# HELPERS
# ==========================================================

def owner(user_id: int):
    return user_id == OWNER_ID

# ==========================================================
# START
# ==========================================================

@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):

    await add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    text = f"""
👋 **Welcome {message.from_user.first_name}!**

I'm **AniToon Bot**.

I can help you:

✏ Rename files

🎬 Convert media

📝 Instant Edit

📄 Media Information

🖼 Custom Thumbnail

🤖 Auto Thumbnail

📊 Progress Bar

👥 Queue System

Choose an option below.
"""

    await send_clean(
        message,
        text,
        reply_markup=start_buttons()
    )

# ==========================================================
# HELP
# ==========================================================

@bot.on_message(filters.private & filters.command("help"))
async def help_cmd(client, message):

    await send_clean(
        message,
        HELP_TEXT,
        reply_markup=help_buttons()
    )

# ==========================================================
# ABOUT
# ==========================================================

@bot.on_message(filters.private & filters.command("about"))
async def about_cmd(client, message):

    text = f"""
🤖 **AniToon Bot**

Production Ready Rename & Convert Bot

Creator:
@MonkeyDLuffy_Prince

Powered By:
https://t.me/Anitoon_edit

Updates:
{CHANNEL_POST}
"""

    await send_clean(
        message,
        text,
        reply_markup=about_buttons()
    )

# ==========================================================
# SETTINGS
# ==========================================================

@bot.on_message(filters.private & filters.command("settings"))
async def settings(client, message):

    if not owner(message.from_user.id):

        return await message.reply_text(
            "❌ Only the bot owner can access settings."
        )

    await send_clean(
        message,
        "⚙ Owner Settings",
        reply_markup=settings_buttons()
    )

# ==========================================================
# PING
# ==========================================================

@bot.on_message(filters.private & filters.command("ping"))
async def ping(client, message):

    await message.reply_text("🏓 Pong!")

# ==========================================================
# ALIVE
# ==========================================================

@bot.on_message(filters.private & filters.command("alive"))
async def alive(client, message):

    await message.reply_text("✅ Bot Online")

