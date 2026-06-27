# ==========================================================
# 🤖 AniToon Bot
# Main Entry Point (Part 1/3)
# ==========================================================

import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters

from engine import process_pipeline
from jobs import create_job
from queue_system import add_to_queue, start_queue

# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

PORT = int(os.environ.get("PORT", 10000))

# ==========================================================
# FLASK WEB SERVER
# (Required for Render/Koyeb/Railway)
# ==========================================================

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 AniToon Bot is Running"

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
# BASIC COMMANDS
# ==========================================================

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):

    await message.reply_text(
        "👋 Welcome to AniToon Bot!\n\n"
        "📤 Send me a video or document to start processing."
    )


@bot.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):

    await message.reply_text(
        "📖 Help\n\n"
        "• Send a Video or Document.\n"
        "• The bot will automatically process it.\n"
        "• Files are handled through the processing queue."
    )

# ==========================================================
# FILE HANDLER
# ==========================================================

@bot.on_message((filters.document | filters.video) & filters.private)
async def handle_file(client, message):

    job_id = str(message.id)
    uid = message.from_user.id

    # ------------------------------------------
    # Create Job
    # ------------------------------------------
    create_job(
        job_id=job_id,
        uid=uid,
        data={
            "new_name": None,
            "mode": "rename",
            "thumb_mode": "auto",
        }
    )

    await message.reply_text(
        "📥 Your file has been added to the processing queue..."
    )

    # ------------------------------------------
    # Queue Handler
    # ------------------------------------------
    async def handler():
        await process_pipeline(job_id, message, client)

    await add_to_queue({
        "uid": uid,
        "handler": handler
    })


# ==========================================================
# BOT EVENTS
# ==========================================================

@bot.on_message(filters.command("ping") & filters.private)
async def ping_cmd(client, message):

    await message.reply_text("🏓 Pong!")


@bot.on_message(filters.command("alive") & filters.private)
async def alive_cmd(client, message):

    await message.reply_text("✅ AniToon Bot is Online")

# ==========================================================
# STARTUP FUNCTIONS
# ==========================================================

def run_queue():

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start the queue processor
    start_queue()

    loop.run_forever()


def run_bot():

    bot.run()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("🚀 AniToon Bot Starting...")
    print("=" * 50)

    # Queue Thread
    threading.Thread(
        target=run_queue,
        daemon=True
    ).start()

    # Telegram Bot Thread
    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()
def run_bot():
    bot.run()
    # Flask Web Server (Render/Koyeb/Railway)
    app.run(
        host="0.0.0.0",
        port=PORT
    )
