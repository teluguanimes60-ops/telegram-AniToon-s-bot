# ==========================================================
# 🤖 AniToon Bot
# Main Bot (Part 1/5)
# Core Initialization & Basic Commands
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

# ==========================================================
# LOCAL IMPORTS
# ==========================================================

from buttons import (
    start_buttons,
    help_buttons,
    about_buttons,
    settings_buttons,
    file_buttons,
    convert_buttons,
    thumbnail_buttons
)

from help_text import HELP_TEXT

from cleaner import send_clean

from db import (
    add_user,
    get_setting,
    set_setting
)

from jobs import (
    create_job,
    get_job,
    update_job,
    delete_job,
    job_exists
)

from queue_system import (
    add_to_queue,
    active_count,
    queue_size,
    user_processing,
    start_queue
)

from states import (
    set_state,
    get_state,
    clear_state,
    has_state
)

from engine import process_pipeline

from instant_edit import (
    instant_edit_caption
)

from media_info import (
    build_media_text
)

# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

PORT = int(os.environ.get("PORT", "10000"))

CHANNEL_POST = "https://t.me/Anitoon_edit/33"

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "✅ AniToon Bot Running"


# ==========================================================
# PYROGRAM CLIENT
# ==========================================================

bot = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================================
# OWNER CHECK
# ==========================================================

def is_owner(user_id: int):
    return user_id == OWNER_ID


# ==========================================================
# /START
# ==========================================================

@bot.on_message(filters.private & filters.command("start"))
async def start_command(client, message):

    await add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    clear_state(message.from_user.id)

    text = f"""
👋 Welcome **{message.from_user.first_name}**

I'm **AniToon Bot** 🤖

━━━━━━━━━━━━━━━━━━

✅ Rename Files

✅ Convert Media

✅ Instant Edit

✅ Media Information

✅ Auto Thumbnail

✅ Custom Thumbnail

✅ Queue System

✅ Live Progress

━━━━━━━━━━━━━━━━━━

👥 Active Users : **{active_count()}**

📋 Waiting Queue : **{queue_size()}**

Choose an option below.
"""

    await send_clean(
        message,
        text,
        reply_markup=start_buttons()
    )


# ==========================================================
# /HELP
# ==========================================================

@bot.on_message(filters.private & filters.command("help"))
async def help_command(client, message):

    await send_clean(
        message,
        HELP_TEXT,
        reply_markup=help_buttons()
    )


# ==========================================================
# /ABOUT
# ==========================================================

@bot.on_message(filters.private & filters.command("about"))
async def about_command(client, message):

    text = f"""
🤖 <b>AniToon Bot</b>

Production Ready Rename & Convert Bot

━━━━━━━━━━━━━━━━━━

👨‍💻 <b>Creator</b>

@MonkeyDLuffy_Prince

━━━━━━━━━━━━━━━━━━

🚀 <b>Powered By</b>

AniToon Edit

https://t.me/Anitoon_edit

━━━━━━━━━━━━━━━━━━

📢 <b>Updates Channel</b>

{CHANNEL_POST}
"""

    await send_clean(
        message,
        text,
        reply_markup=about_buttons()
    )


# ==========================================================
# /SETTINGS
# ==========================================================

@bot.on_message(filters.private & filters.command("settings"))
async def settings_command(client, message):

    if not is_owner(message.from_user.id):

        return await message.reply_text(
            "❌ Only the bot owner can open Settings."
        )

    await send_clean(
        message,
        "⚙️ <b>Owner Settings</b>\n\nChoose an option.",
        reply_markup=settings_buttons()
    )


# ==========================================================
# /PING
# ==========================================================

@bot.on_message(filters.private & filters.command("ping"))
async def ping_command(client, message):

    await message.reply_text("🏓 Pong!")


# ==========================================================
# /ALIVE
# ==========================================================

@bot.on_message(filters.private & filters.command("alive"))
async def alive_command(client, message):

    await message.reply_text(
        "✅ AniToon Bot is Online."
    )

# ==========================================================
# END OF PART 1
# Part 2:
# Callback Query Handlers
# Home / Help / About / Settings
# Back Navigation
# ==========================================================

# ==========================================================
# CALLBACK QUERY HANDLERS
# Part 2A/5
# Home • Help • About • Settings • Back Navigation
# ==========================================================

from pyrogram import filters
from pyrogram.types import CallbackQuery

# ==========================================================
# HOME
# ==========================================================

@bot.on_callback_query(filters.regex("^home$"))
async def home_callback(client, query: CallbackQuery):

    text = f"""
👋 Welcome **{query.from_user.first_name}**

I'm **AniToon Bot**

━━━━━━━━━━━━━━━━━━

✏ Rename Files

🎬 Convert Media

📝 Instant Edit

📄 Media Information

🖼 Thumbnail Support

📊 Live Progress

👥 Queue System

━━━━━━━━━━━━━━━━━━

👥 Active Users : **{active_count()}**

📋 Waiting Queue : **{queue_size()}**

Choose an option below.
"""

    await query.message.edit_text(
        text,
        reply_markup=start_buttons()
    )

    await query.answer()


# ==========================================================
# HELP
# ==========================================================

@bot.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query: CallbackQuery):

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=help_buttons()
    )

    await query.answer()


# ==========================================================
# ABOUT
# ==========================================================

@bot.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query: CallbackQuery):

    text = f"""
🤖 <b>AniToon Bot</b>

━━━━━━━━━━━━━━━━━━

Production Ready Rename &
Convert Telegram Bot

━━━━━━━━━━━━━━━━━━

👨‍💻 <b>Creator</b>

@MonkeyDLuffy_Prince

━━━━━━━━━━━━━━━━━━

🚀 <b>Powered By</b>

AniToon Edit

https://t.me/Anitoon_edit

━━━━━━━━━━━━━━━━━━

📢 Updates

{CHANNEL_POST}
"""

    await query.message.edit_text(
        text,
        reply_markup=about_buttons()
    )

    await query.answer()


# ==========================================================
# SETTINGS
# ==========================================================

@bot.on_callback_query(filters.regex("^settings$"))
async def settings_callback(client, query: CallbackQuery):

    if not is_owner(query.from_user.id):

        return await query.answer(
            "Only Bot Owner can access Settings.",
            show_alert=True
        )

    await query.message.edit_text(
        "⚙ **Owner Settings**\n\nChoose an option.",
        reply_markup=settings_buttons()
    )

    await query.answer()


# ==========================================================
# SETTINGS : THUMBNAIL
# ==========================================================

@bot.on_callback_query(filters.regex("^settings_thumb$"))
async def settings_thumb(client, query: CallbackQuery):

    await query.message.edit_text(
        "🖼 Thumbnail settings will be configured here.",
        reply_markup=settings_buttons()
    )

    await query.answer()


# ==========================================================
# SETTINGS : CLEANER
# ==========================================================

@bot.on_callback_query(filters.regex("^settings_clean$"))
async def settings_clean(client, query: CallbackQuery):

    await query.message.edit_text(
        "🧹 Chat cleaner is enabled.\n\n"
        "Old bot and user messages will be deleted automatically.",
        reply_markup=settings_buttons()
    )

    await query.answer()


# ==========================================================
# BACK TO HOME
# ==========================================================

@bot.on_callback_query(filters.regex("^back_home$"))
async def back_home(client, query: CallbackQuery):

    text = f"""
👋 Welcome **{query.from_user.first_name}**

Choose an option below.

👥 Active Users : **{active_count()}**

📋 Waiting Queue : **{queue_size()}**
"""

    await query.message.edit_text(
        text,
        reply_markup=start_buttons()
    )

    await query.answer()


# ==========================================================
# IGNORE UNKNOWN CALLBACKS
# ==========================================================

@bot.on_callback_query()
async def ignore_unknown_callback(client, query: CallbackQuery):
    try:
        await query.answer()
    except:
        pass

# ==========================================================
# END OF PART 2A
#
# Next:
# Part 2B
#
# ✅ Rename
# ✅ Convert
# ✅ Instant Edit
# ✅ Media Info
# ✅ Thumbnail Selection
# ==========================================================

        # ==========================================================
# CALLBACKS
# Part 2B-1/5
# File Menu + Convert Menu
# ==========================================================

# ----------------------------------------------------------
# FILE MENU
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^file_menu$"))
async def file_menu_callback(client, query):

    await query.message.edit_text(
        "📂 <b>Choose what you want to do with your file.</b>",
        reply_markup=file_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# RENAME
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^rename$"))
async def rename_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" not in state:

        return await query.answer(
            "❌ Send a file first.",
            show_alert=True
        )

    set_state(
        uid,
        **state,
        mode="rename",
        step="rename_name"
    )

    await query.message.edit_text(
        "✏️ <b>Rename Mode</b>\n\n"
        "Now send the new filename.\n\n"
        "Example:\n"
        "<code>One Piece Episode 1135</code>"
    )

    await query.answer()


# ----------------------------------------------------------
# CONVERT
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^convert$"))
async def convert_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" not in state:

        return await query.answer(
            "❌ Send a file first.",
            show_alert=True
        )

    await query.message.edit_text(
        "🎬 <b>Select Conversion Type</b>",
        reply_markup=convert_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# CONVERT -> VIDEO
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^convert_video$"))
async def convert_video_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" not in state:
        return await query.answer(
            "No active job.",
            show_alert=True
        )

    update_job(
        state["job_id"],
        "mode",
        "video"
    )

    await query.message.edit_text(
        "🖼 Select Thumbnail Option",
        reply_markup=thumbnail_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# CONVERT -> DOCUMENT
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^convert_document$"))
async def convert_document_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" not in state:
        return await query.answer(
            "No active job.",
            show_alert=True
        )

    update_job(
        state["job_id"],
        "mode",
        "document"
    )

    await query.message.edit_text(
        "🖼 Select Thumbnail Option",
        reply_markup=thumbnail_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# CONVERT -> AUDIO
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^convert_audio$"))
async def convert_audio_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" not in state:
        return await query.answer(
            "No active job.",
            show_alert=True
        )

    update_job(
        state["job_id"],
        "mode",
        "audio"
    )

    await query.message.edit_text(
        "🖼 Select Thumbnail Option",
        reply_markup=thumbnail_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# BACK TO FILE MENU
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^back_file$"))
async def back_file_callback(client, query):

    await query.message.edit_text(
        "📂 <b>Choose an option.</b>",
        reply_markup=file_buttons()
    )

    await query.answer()

# ==========================================================
# END OF PART 2B-1
# Next: Part 2B-2
# • Thumbnail callbacks
# • Instant Edit
# • Media Info
# • Cancel
# • Continue processing
# ==========================================================

# ==========================================================
# CALLBACKS
# Part 2B-2/5
# Thumbnail • Instant Edit • Media Info • Cancel
# ==========================================================

# ----------------------------------------------------------
# CUSTOM THUMBNAIL
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^thumb_custom$"))
async def thumb_custom_callback(client, query):

    uid = query.from_user.id
    state = get_state(uid)

    set_state(
        uid,
        **state,
        thumb_mode="saved",
        step="waiting_thumbnail"
    )

    await query.message.edit_text(
        "🖼 <b>Custom Thumbnail</b>\n\n"
        "Send me a photo.\n\n"
        "It will be saved permanently for future uploads."
    )

    await query.answer()


# ----------------------------------------------------------
# AUTO THUMBNAIL
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^thumb_auto$"))
async def thumb_auto_callback(client, query):

    uid = query.from_user.id
    state = get_state(uid)

    if "job_id" in state:
        update_job(
            state["job_id"],
            "thumb_mode",
            "auto"
        )

    await query.message.edit_text(
        "✅ Auto Thumbnail selected.\n\n"
        "Press Continue."
    )

    await query.answer()


# ----------------------------------------------------------
# WITHOUT THUMBNAIL
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^thumb_none$"))
async def thumb_none_callback(client, query):

    uid = query.from_user.id
    state = get_state(uid)

    if "job_id" in state:
        update_job(
            state["job_id"],
            "thumb_mode",
            "none"
        )

    await query.message.edit_text(
        "🚫 Thumbnail disabled.\n\n"
        "Press Continue."
    )

    await query.answer()


# ----------------------------------------------------------
# CONTINUE
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^thumb_continue$"))
async def thumb_continue_callback(client, query):

    await query.message.edit_text(
        "⏳ Added to queue.\n\n"
        "Processing will begin automatically."
    )

    await query.answer("Queued")


# ----------------------------------------------------------
# INSTANT EDIT
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^instant_edit$"))
async def instant_edit_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    set_state(
        uid,
        **state,
        step="instant_edit"
    )

    await query.message.edit_text(
        "📝 <b>Instant Edit</b>\n\n"
        "Send the new caption.\n\n"
        "The bot will edit the uploaded file caption without downloading or uploading again."
    )

    await query.answer()


# ----------------------------------------------------------
# MEDIA INFO
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^media_info$"))
async def media_info_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "file_path" not in state:

        return await query.answer(
            "No downloaded file available.",
            show_alert=True
        )

    text = build_media_text(
        state["file_path"]
    )

    await query.message.edit_text(
        text
    )

    await query.answer()


# ----------------------------------------------------------
# CANCEL
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^cancel$"))
async def cancel_callback(client, query):

    uid = query.from_user.id

    clear_state(uid)

    await query.message.edit_text(
        "❌ Operation cancelled.",
        reply_markup=start_buttons()
    )

    await query.answer()


# ----------------------------------------------------------
# CANCEL ACTIVE JOB
# ----------------------------------------------------------

@bot.on_callback_query(filters.regex("^cancel_job$"))
async def cancel_job_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" in state:

        delete_job(state["job_id"])

    clear_state(uid)

    await query.message.edit_text(
        "❌ Job cancelled successfully.",
        reply_markup=start_buttons()
    )

    await query.answer()

# ==========================================================
# END OF PART 2
#
# Part 3 will contain:
#
# ✅ File handler
# ✅ Queue entry
# ✅ One active job per user
# ✅ Maximum 20 users
# ✅ Duplicate protection
# ✅ Auto delete old messages
# ✅ Rename input
# ✅ Instant Edit input
# ✅ Custom Thumbnail upload
# ==========================================================

