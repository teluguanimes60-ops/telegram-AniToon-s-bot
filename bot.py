# ==========================================================

# 🤖 AniToon Bot

# ==========================================================

import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.INFO)

import os

import asyncio

import threading

from db import init_database

from flask import Flask



from pyrogram import Client, filters, idle

from pyrogram.types import (

    InlineKeyboardMarkup,

    InlineKeyboardButton

)



from buttons import (

    start_buttons,

    help_buttons,

    about_buttons,

    owner_settings_buttons,

    file_buttons,

    convert_buttons,

    video_thumbnail_buttons,

    document_thumbnail_buttons,

    download_buttons,

    upload_buttons

)



from help_text import HELP_TEXT



from cleaner import (

    send_clean,

    save_user_message,

    clean_chat

)



from db import (

    add_user,

    set_setting

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



CHANNEL_POST = "https://t.me/Anitoon_edit"



# ==========================================================

# FLASK

# ==========================================================



app = Flask(__name__)





@app.route("/")

def home():

    return "AniToon Bot Running ✅"





# ==========================================================

# BOT

# ==========================================================
import logging

logging.basicConfig(level=logging.INFO)

bot = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ==========================================================

# HELPERS

# ==========================================================



def is_owner(uid):

    return uid == OWNER_ID





# ==========================================================

# START

# ==========================================================



@bot.on_message(filters.private & filters.command("start"))

async def start_cmd(client, message):



    await save_user_message(message.from_user.id, message)



    await add_user(

        message.from_user.id,

        message.from_user.first_name

    )



    clear_state(message.from_user.id)



    text = f"""

👋 Welcome **{message.from_user.first_name}**



I'm **AniToon Bot**



━━━━━━━━━━━━━━━━━━



✏️ Rename Files



🎬 Convert Files



📝 Instant Edit



📄 Media Information



🖼 Thumbnail Support



📊 Queue System



━━━━━━━━━━━━━━━━━━



Choose an option below.

"""



    await send_clean(

        message,

        text,

        reply_markup=start_buttons(

            is_owner(message.from_user.id)

        )

    )





# ==========================================================

# HELP

# ==========================================================



@bot.on_message(filters.private & filters.command("help"))

async def help_cmd(client, message):



    await save_user_message(message.from_user.id, message)



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



    await save_user_message(message.from_user.id, message)



    text = f"""

🤖 **AniToon Bot**



Rename • Convert • Instant Edit



━━━━━━━━━━━━━━━━━━



👨‍💻 Developer



@MonkeyDLuffy_Prince



━━━━━━━━━━━━━━━━━━



📢 Channel



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



    await save_user_message(message.from_user.id, message)



    if not is_owner(message.from_user.id):

        return await send_clean(

            message,

            "❌ Only Bot Owner can access Settings."

        )



    await send_clean(

        message,

        "⚙️ **Owner Settings**",

        reply_markup=owner_settings_buttons()

    )





# ==========================================================

# PING

# ==========================================================



@bot.on_message(filters.private & filters.command("ping"))

async def ping_cmd(client, message):



    await save_user_message(message.from_user.id, message)



    await send_clean(

        message,

        "🏓 Pong!"

    )





# ==========================================================

# ALIVE

# ==========================================================



@bot.on_message(filters.private & filters.command("alive"))

async def alive_cmd(client, message):



    await save_user_message(message.from_user.id, message)



    await send_clean(

        message,

        "✅ AniToon Bot is Online."

    )
    
@bot.on_callback_query(filters.regex("^home$"))
async def home_callback(client, query):

    clear_state(query.from_user.id)

    text = f"""
👋 Welcome **{query.from_user.first_name}**

I'm **AniToon Bot**

━━━━━━━━━━━━━━━━━━

📊 Live Progress
👥 Queue System

━━━━━━━━━━━━━━━━━━

Choose an option below.
"""

    await query.message.edit_text(
        text,
        reply_markup=start_buttons(
            is_owner(query.from_user.id)
        )
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
        reply_markup=owner_settings_buttons()
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
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="home"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="cancel"
                )
            ]
        ])
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
        "🎬 Choose Conversion Type",
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

        wait = await send_clean(
            message,
            "📥 Downloading file..."
        )

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

        return await send_clean(
            message,
            "❌ Select **Rename** or **Convert** from the menu first."
        )

    if user_processing(uid):

        return await send_clean(
            message,
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

    await send_clean(
        message,
        "✏️ Send the new filename.\n\n"
        "Example:\n"
        "`One Piece Episode 1135`",
        disable_web_page_preview=True
    )


# ==========================================================
# RECEIVE TEXT
# ==========================================================

@bot.on_message(
    filters.private
    & filters.text
    & ~filters.command([
        "start",
        "help",
        "about",
        "ping",
        "alive",
        "settings"
    ])
)
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

        return await send_clean(
            message,
            msg
        )

    # ---------------- WAITING NEW NAME ----------------

    if state.get("step") != "waiting_name":
        return

    job = get_job(state["job_id"])

    if not job:

        clear_state(uid)

        return await send_clean(
            message,
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

    await send_clean(
        message,
        "🖼 Choose Thumbnail Mode",
        reply_markup=video_thumbnail_buttons()
    )


# ==========================================================
# THUMBNAIL CALLBACKS
# ==========================================================
@bot.on_message(filters.command("test"))
async def test(client, message):
    print("TEST RECEIVED")
    await message.reply("Working!")
    
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

# ==========================================================
# 🤖 AniToon Bot
# bot.py (Part 4/5)
# ==========================================================

from thumbnail import save_thumb
from db import set_setting

# ==========================================================
# PAUSE
# ==========================================================

@bot.on_callback_query(filters.regex("^pause$"))
async def pause_callback(client, query):

    uid = query.from_user.id

    set_state(uid, paused=True)

    await query.answer(
        "⏸ Download Paused",
        show_alert=True
    )


# ==========================================================
# RESUME
# ==========================================================

@bot.on_callback_query(filters.regex("^resume$"))
async def resume_callback(client, query):

    uid = query.from_user.id

    set_state(uid, paused=False)

    await query.answer(
        "▶ Download Resumed",
        show_alert=True
    )


# ==========================================================
# CANCEL
# ==========================================================

@bot.on_callback_query(filters.regex("^(cancel|cancel_job)$"))
async def cancel_callback(client, query):

    uid = query.from_user.id

    state = get_state(uid)

    if "job_id" in state:
        delete_job(state["job_id"])

    clear_state(uid)

    await query.message.edit_text(
        "❌ Job Cancelled Successfully."
    )

    await query.answer()


# ==========================================================
# OWNER SETTINGS
# ==========================================================

@bot.on_callback_query(filters.regex("^settings_thumb$"))
async def owner_thumb(client, query):

    if not is_owner(query.from_user.id):
        return await query.answer(
            "Owner Only",
            show_alert=True
        )

    await query.message.edit_text(
        "🖼 Default Thumbnail Settings\n\n"
        "Choose the default thumbnail mode.",
        reply_markup=document_thumbnail_buttons()
    )

    await query.answer()


@bot.on_callback_query(filters.regex("^settings_clean$"))
async def owner_clean(client, query):

    if not is_owner(query.from_user.id):
        return await query.answer(
            "Owner Only",
            show_alert=True
        )

    await set_setting(
        query.from_user.id,
        "auto_clean",
        True
    )

    await query.answer(
        "✅ Auto Cleaner Enabled",
        show_alert=True
    )


# ==========================================================
# SAVE CUSTOM THUMBNAIL
# ==========================================================

@bot.on_message(filters.private & filters.photo)
async def save_custom_thumb(client, message):

    uid = message.from_user.id
    state = get_state(uid)

    if state.get("step") != "waiting_custom_thumb":
        return

    job_id = state.get("job_id")

    if not job_id:
        clear_state(uid)

        return await send_clean(
            message,
            "❌ Job expired."
        )

    await save_thumb(
        client,
        uid,
        message.photo.file_id
    )

    update_job(job_id, "thumb_mode", "saved")

    clear_state(uid)

    await send_clean(
        message,
        "✅ Custom Thumbnail Saved.\n\n📥 Added to Queue..."
    )

    job = get_job(job_id)

    if not job:
        return

    await add_to_queue({
        "uid": uid,
        "handler": lambda: process_pipeline(
            job_id,
            job["original_message"],
            bot
        )
    })


# ==========================================================
# UNKNOWN COMMAND
# ==========================================================

@bot.on_message(filters.private & filters.command)
async def unknown(client, message):

    await send_clean(
        message,
        "❌ Unknown command.\n\nUse /start"
    )

    # ==========================================================
# 🤖 AniToon Bot
# bot.py (Part 5/5)
# ==========================================================

# ==========================================================
# START QUEUE
# ==========================================================

async def queue_runner():

    try:
        await start_queue()

    except Exception as e:
        print("QUEUE ERROR :", e)


# ==========================================================
# START BOT
# ==========================================================

async def bot_runner():

    print("Starting Telegram Bot...")

    await bot.start()

    me = await bot.get_me()
print(f"Logged in as @{me.username}")

    print("Bot connected!")

    await init_database()

    await start_queue()

    print("Queue Started!")

    await idle()

    await bot.stop()
    
# ==========================================================
# FLASK THREAD
# ==========================================================

def run_web():

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    asyncio.run(bot_runner())
