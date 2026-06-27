# ==========================================================
# 🤖 AniToon Bot
# bot.py (Part 1/5)
# ==========================================================

import os
import asyncio
import threading

from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

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
    add_user
)

from states import (
    set_state,
    get_state,
    clear_state
)

from jobs import (
    create_job,
    get_job,
    update_job,
    delete_job
)

from queue_system import (
    add_to_queue,
    active_count,
    queue_size,
    user_processing,
    start_queue
)

from engine import process_pipeline

from instant_edit import (
    save_editable_message,
    instant_edit_caption
)

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
# HELPERS
# ==========================================================

def is_owner(user_id: int):
    return user_id == OWNER_ID


# ==========================================================
# START
# ==========================================================

@bot.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):

    await add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    clear_state(message.from_user.id)

    text = f"""
👋 Welcome **{message.from_user.first_name}**

I'm **AniToon Bot**

━━━━━━━━━━━━━━━━━━

✏ Rename Files

🎬 Convert Files

📝 Instant Edit

📄 Media Information

🖼 Thumbnail Support

📊 Live Progress

👥 Queue System

━━━━━━━━━━━━━━━━━━

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

━━━━━━━━━━━━━━━━━━

👨‍💻 Creator

@MonkeyDLuffy_Prince

━━━━━━━━━━━━━━━━━━

🚀 Powered By

https://t.me/Anitoon_edit

━━━━━━━━━━━━━━━━━━

📢 Updates

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
async def settings_cmd(client, message):

    if not is_owner(message.from_user.id):

        return await message.reply_text(
            "❌ Only the Bot Owner can access Settings."
        )

    await send_clean(
        message,
        "⚙ **Owner Settings**",
        reply_markup=settings_buttons()
    )


# ==========================================================
# PING
# ==========================================================

@bot.on_message(filters.private & filters.command("ping"))
async def ping_cmd(client, message):

    await message.reply_text("🏓 Pong!")


# ==========================================================
# ALIVE
# ==========================================================

@bot.on_message(filters.private & filters.command("alive"))
async def alive_cmd(client, message):

    await message.reply_text(
        "✅ AniToon Bot is Online."
    )

    # ==========================================================
# CALLBACK QUERIES
# bot.py (Part 2/5)
# ==========================================================

@bot.on_callback_query(filters.regex("^home$"))
async def home_callback(client, query):

    clear_state(query.from_user.id)

    text = f"""
👋 Welcome **{query.from_user.first_name}**

I'm **AniToon Bot**

━━━━━━━━━━━━━━━━━━

✏ Rename Files

🎬 Convert Files

📝 Instant Edit

📄 Media Information

🖼 Thumbnail Support

📊 Live Progress

👥 Queue System

━━━━━━━━━━━━━━━━━━

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
async def help_callback(client, query):

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=help_buttons()
    )

    await query.answer()


# ==========================================================
# ABOUT
# ==========================================================

@bot.on_callback_query(filters.regex("^about$"))
async def about_callback(client, query):

    text = f"""
🤖 **AniToon Bot**

Production Ready Rename & Convert Bot

━━━━━━━━━━━━━━━━━━

👨‍💻 Creator

@MonkeyDLuffy_Prince

━━━━━━━━━━━━━━━━━━

🚀 Powered By

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
async def settings_callback(client, query):

    if not is_owner(query.from_user.id):

        await query.answer(
            "Only Bot Owner",
            show_alert=True
        )
        return

    await query.message.edit_text(
        "⚙ **Owner Settings**",
        reply_markup=settings_buttons()
    )

    await query.answer()


# ==========================================================
# FILE MENU
# ==========================================================

@bot.on_callback_query(filters.regex("^rename$"))
async def rename_callback(client, query):

    uid = query.from_user.id

    set_state(
        uid,
        mode="rename",
        step="waiting_file"
    )

    await query.message.edit_text(
        "📤 Send the file you want to rename.",
        reply_markup=file_buttons()
    )

    await query.answer()


# ==========================================================
# CONVERT MENU
# ==========================================================

@bot.on_callback_query(filters.regex("^convert$"))
async def convert_callback(client, query):

    uid = query.from_user.id

    set_state(
        uid,
        mode="convert",
        step="select_convert"
    )

    await query.message.edit_text(
        "🎬 Choose Convert Mode",
        reply_markup=convert_buttons()
    )

    await query.answer()


# ==========================================================
# INSTANT EDIT
# ==========================================================

@bot.on_callback_query(filters.regex("^instant_edit$"))
async def instant_edit_callback(client, query):

    uid = query.from_user.id

    set_state(
        uid,
        mode="instant_edit",
        step="waiting_caption"
    )

    await query.message.edit_text(
        "📝 Send the new filename/caption.\n\n"
        "No download.\n"
        "No upload.\n"
        "The latest uploaded media caption will be edited instantly."
    )

    await query.answer()


# ==========================================================
# MEDIA INFO
# ==========================================================

@bot.on_callback_query(filters.regex("^media_info$"))
async def media_info_callback(client, query):

    uid = query.from_user.id

    set_state(
        uid,
        mode="media_info",
        step="waiting_file"
    )

    await query.message.edit_text(
        "📄 Send a media file to view complete Media Information."
    )

    await query.answer()


# ==========================================================
# BACK TO FILE MENU
# ==========================================================

@bot.on_callback_query(filters.regex("^back_file$"))
async def back_file(client, query):

    await query.message.edit_text(
        "Choose an option.",
        reply_markup=file_buttons()
    )

    await query.answer()


# ==========================================================
# BACK TO CONVERT MENU
# ==========================================================

@bot.on_callback_query(filters.regex("^back_convert$"))
async def back_convert(client, query):

    await query.message.edit_text(
        "🎬 Choose Convert Mode",
        reply_markup=convert_buttons()
    )

    await query.answer()

# ==========================================================
# FILE RECEIVER
# bot.py (Part 3/5)
# ==========================================================

from media_info import build_media_text


@bot.on_message(filters.private & (filters.document | filters.video))
async def receive_file(client, message):

    uid = message.from_user.id
    state = get_state(uid)

    # Save for Instant Edit
    save_editable_message(uid, message)

    # ---------------- MEDIA INFO ----------------

    if state.get("mode") == "media_info":

        wait = await message.reply_text("📥 Downloading file...")

        path = await message.download()

        try:
            text = build_media_text(path)

            await wait.edit_text(text)

        finally:
            import os
            if path and os.path.exists(path):
                os.remove(path)

        clear_state(uid)
        return

    # ---------------- RENAME / CONVERT ----------------

    if state.get("mode") not in ["rename", "convert"]:

        return await message.reply_text(
            "❌ Select **Rename** or **Convert** from the menu first."
        )

    if user_processing(uid):

        return await message.reply_text(
            "⚠️ You already have an active job."
        )

    job_id = str(message.id)

    create_job(
        job_id=job_id,
        uid=uid,
        data={
            "mode": state.get("mode"),
            "thumb_mode": "auto",
            "original_message": message
        }
    )

    set_state(
        uid,
        step="waiting_name",
        job_id=job_id
    )

    await message.reply_text(
        "✏️ Send the new filename.\n\n"
        "Example:\n"
        "`One Piece Episode 1135`",
        disable_web_page_preview=True
    )


# ==========================================================
# RECEIVE TEXT
# ==========================================================

@bot.on_message(filters.private & filters.text)
async def receive_text(client, message):

    uid = message.from_user.id
    state = get_state(uid)

    # ---------------- INSTANT EDIT ----------------

    if state.get("mode") == "instant_edit":

        ok, msg = await instant_edit_caption(
            client,
            uid,
            message.text
        )

        clear_state(uid)

        return await message.reply_text(msg)

    # ---------------- WAITING NEW NAME ----------------

    if state.get("step") != "waiting_name":
        return

    job = get_job(state["job_id"])

    if not job:
        clear_state(uid)
        return await message.reply_text(
            "❌ Job expired."
        )

    update_job(
        state["job_id"],
        "new_name",
        message.text.strip()
    )

    set_state(
        uid,
        step="waiting_thumbnail",
        job_id=state["job_id"]
    )

    await message.reply_text(
        "🖼 Choose Thumbnail Mode",
        reply_markup=thumbnail_buttons()
    )


# ==========================================================
# THUMBNAIL CALLBACKS
# ==========================================================

@bot.on_callback_query(filters.regex("^thumb_"))
async def thumbnail_callbacks(client, query):

    uid = query.from_user.id
    state = get_state(uid)

    if "job_id" not in state:
        return await query.answer("Job expired.")

    job_id = state["job_id"]

    data = query.data

    if data == "thumb_custom":

        update_job(job_id, "thumb_mode", "saved")

        await query.message.edit_text(
            "📤 Send your thumbnail image (.jpg/.png)."
        )

        set_state(
            uid,
            step="waiting_custom_thumb",
            job_id=job_id
        )

    elif data == "thumb_auto":

        update_job(job_id, "thumb_mode", "auto")

        await query.message.edit_text(
            "✅ Auto Thumbnail Selected.\n\nStarting Queue..."
        )

        await start_processing(job_id)

    elif data == "thumb_none":

        update_job(job_id, "thumb_mode", "none")

        await query.message.edit_text(
            "✅ Thumbnail Disabled.\n\nStarting Queue..."
        )

        await start_processing(job_id)

    elif data == "thumb_continue":

        await start_processing(job_id)

    await query.answer()


# ==========================================================
# CUSTOM THUMB RECEIVER
# ==========================================================

@bot.on_message(filters.private & filters.photo)
async def custom_thumb(client, message):

    uid = message.from_user.id
    state = get_state(uid)

    if state.get("step") != "waiting_custom_thumb":
        return

    from thumbnail import save_thumb

    photo = message.photo.file_id

    await save_thumb(uid, photo)

    job_id = state["job_id"]

    update_job(job_id, "thumb_mode", "saved")

    await message.reply_text(
        "✅ Thumbnail Saved.\n\nStarting Queue..."
    )

    await start_processing(job_id)


# ==========================================================
# START PROCESSING
# ==========================================================

async def start_processing(job_id):

    job = get_job(job_id)

    if not job:
        return

    msg = job["original_message"]

    uid = job["uid"]

    clear_state(uid)

    await add_to_queue({
        "uid": uid,
        "handler": lambda: process_pipeline(
            job_id,
            msg,
            bot
        )
    })

    await msg.reply_text(
        f"📥 Added to Queue\n\n"
        f"👥 Active Users : {active_count()}/20\n"
        f"📋 Waiting : {queue_size()}\n\n"
        f"📢 Subscribe before processing:\n"
        f"{CHANNEL_POST}"
    )
