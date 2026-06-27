# ==========================================================

# 🤖 AniToon Bot

# bot.py (Part 1/5)

# ==========================================================



import os

import asyncio

import threading



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
    
