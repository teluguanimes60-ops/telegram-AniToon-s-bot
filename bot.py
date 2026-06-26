# ==========================================
# AniToon Bot - FINAL STABLE bot.py
# FIXED: asyncio loop + render + queue + threads
# ==========================================

import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters

from engine import process_pipeline
from queue_system import start_queue

# ---------------- ENV ----------------
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ---------------- FLASK (KEEP ALIVE ONLY) ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 AniToon Bot is Running"

# ---------------- PYROGRAM BOT ----------------
bot = Client(
    "anitoon-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- HANDLER ----------------
@bot.on_message(filters.document | filters.video)
async def handle_file(client, message):

    job_id = str(message.id)

    # safe async task (no blocking)
    asyncio.create_task(process_pipeline(job_id, message, client))

# ---------------- QUEUE LOOP ----------------
def run_queue():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(start_queue())
    loop.run_forever()

# ---------------- BOT LOOP ----------------
def run_bot():
    bot.run()

# ---------------- MAIN START ----------------
if __name__ == "__main__":

    print("🚀 FINAL PLATFORM BOT STARTED")

    # start queue thread
    threading.Thread(target=run_queue, daemon=True).start()

    # start bot thread
    threading.Thread(target=run_bot, daemon=True).start()

    # start flask web server (Render requirement)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
