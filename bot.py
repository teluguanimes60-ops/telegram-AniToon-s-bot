# ==========================================
# AniToon Bot - FINAL ENGINE ROUTER
# ==========================================

import os
import asyncio
import threading

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- CORE ENGINE ----------------
from engine import process_pipeline

# ---------------- JOB + QUEUE ----------------
from jobs import create_job, update_job
from queue_system import start_queue

# ---------------- DB ----------------
from db import add_user

# ---------------- CONFIG ----------------
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("Missing API credentials")

# ---------------- FLASK ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot PLATFORM RUNNING ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

print("🚀 FINAL PLATFORM BOT STARTED")

# ---------------- USER STATE ----------------
user_state = {}

# ---------------- START MENU ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    await add_user(msg.from_user.id)
    await msg.reply_text("👋 Welcome to AniToon File Platform", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def callback(_, q):

    uid = q.from_user.id
    data = q.data

    if data in ["rename", "convert", "instant", "thumb"]:

        user_state[uid] = {"mode": data}

        await q.message.reply_text(f"📥 Send your file for {data}")

    elif data == "help":

        await q.message.reply_text(
            "📌 HELP MENU\n\n"
            "• Rename: change file name\n"
            "• Convert: process file\n"
            "• Instant: fast resend (no download)\n"
            "• Thumbnail: set thumbnail\n\n"
            "Send file to start.",
            reply_markup=main_menu()
        )

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    mode = state["mode"]

    # ---------------- INSTANT MODE ----------------
    if mode == "instant":

        job_id = create_job(uid, msg, "instant")

        await msg.reply_text("⚡ Instant processing...")

        await process_pipeline(job_id, msg, app)

        user_state.pop(uid, None)
        return

    # ---------------- NORMAL MODES ----------------
    job_id = create_job(uid, msg, mode)

    if mode == "rename":
        await msg.reply_text("✏️ Send new name")
        user_state[uid]["job_id"] = job_id

    else:
        await msg.reply_text("📥 Added to processing queue...")

        asyncio.create_task(process_pipeline(job_id, msg, app))

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    job_id = state.get("job_id")

    if not job_id:
        return

    # ---------------- RENAME UPDATE ----------------
    update_job(job_id, "new_name", msg.text)

    await msg.reply_text("✅ Name saved. Processing started...")

    asyncio.create_task(process_pipeline(job_id, msg, app))

    user_state.pop(uid, None)

# ---------------- START QUEUE SYSTEM ----------------
import asyncio
from queue_system import start_queue

loop = asyncio.get_event_loop()
start_queue(loop)

# ---------------- RUN ----------------
app.run()
