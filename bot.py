# ==========================================
# AniToon Bot - FINAL PRODUCTION BUILD
# ==========================================

import os
import time
import asyncio
import threading
import uuid

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- MODULES ----------------
from queue_system import add_user, remove_user, can_process
from jobs import create_job, get_job, update_job, pause_job, resume_job, cancel_job
from progress import progress
from instant_edit import instant_edit
from thumbnail import get_thumb
from auto_thumb import generate_thumbnail, setup_ffmpeg
from help_text import HELP_TEXT

# ---------------- ENV ----------------
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("Missing API credentials")

setup_ffmpeg()

# ---------------- FLASK ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

print("🚀 FINAL BOT STARTED")

# ---------------- MEMORY ----------------
user_state = {}

# ---------------- UI ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def thumb_menu(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Saved", callback_data=f"saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto", callback_data=f"auto_{job_id}")],
        [InlineKeyboardButton("❌ None", callback_data=f"none_{job_id}")]
    ])

def process_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶ Resume", callback_data=f"resume_{job_id}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply_text("👋 Welcome to AniToon Bot", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):

    uid = q.from_user.id
    data = q.data

    if data == "rename":
        user_state[uid] = {"mode": "rename"}
        await q.message.reply_text("📁 Send file to rename")

    elif data == "convert":
        user_state[uid] = {"mode": "convert"}
        await q.message.reply_text("🔄 Send file to convert")

    elif data == "instant":
        user_state[uid] = {"mode": "instant"}
        await q.message.reply_text("⚡ Send file for instant edit")

    elif data == "thumb":
        user_state[uid] = {"mode": "thumb"}
        await q.message.reply_text("🖼 Send thumbnail image")

    elif data == "help":
        await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())

    # ---------------- JOB CONTROLS ----------------
    elif data.startswith("pause_"):
        pause_job(data.split("_")[1])
        await q.answer("Paused")

    elif data.startswith("resume_"):
        resume_job(data.split("_")[1])
        await q.answer("Resumed")

    elif data.startswith("cancel_"):
        cancel_job(data.split("_")[1])
        await q.answer("Cancelled")

    # ---------------- THUMB SELECTION ----------------
    elif data.startswith("saved_"):
        update_job(data.split("_")[1], "thumb_mode", "saved")

    elif data.startswith("auto_"):
        update_job(data.split("_")[1], "thumb_mode", "auto")

    elif data.startswith("none_"):
        update_job(data.split("_")[1], "thumb_mode", "none")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    # ---------------- LIMIT CHECK (20 USERS) ----------------
    if not can_process(uid):
        await msg.reply_text("⛔ 20 users are processing. Please wait few minutes.")
        return

    add_user(uid)

    mode = state["mode"]

    # ---------------- INSTANT MODE ----------------
    if mode == "instant":
        job_id = create_job(uid, msg, "instant")

        await msg.reply_text("⚡ Instant mode activated...")

        await instant_edit(job_id, lambda: msg.text or "file")

        remove_user(uid)
        user_state.pop(uid, None)
        return

    # ---------------- NORMAL JOB ----------------
    job_id = create_job(uid, msg, mode)

    await msg.reply_text(
        "🖼 Choose Thumbnail",
        reply_markup=thumb_menu(job_id)
    )

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    mode = state["mode"]

    # ---------------- RENAME ----------------
    if mode == "rename":

        job_id = create_job(uid, state["file"], "rename")
        update_job(job_id, "new_name", msg.text)

        asyncio.create_task(run_job(job_id))
        user_state.pop(uid, None)

    # ---------------- CONVERT ----------------
    elif mode == "convert":

        job_id = create_job(uid, state["file"], "convert")

        asyncio.create_task(run_job(job_id))
        user_state.pop(uid, None)

# ---------------- MAIN ENGINE ----------------
async def run_job(job_id):

    job = get_job(job_id)
    msg = job["file"]

    status = await msg.reply_text("📥 Starting...", reply_markup=process_buttons(job_id))

    file_path = None

    try:

        file_path = await msg.download(progress=progress, progress_args=(status, time.time()))

        await status.edit_text("⚙️ Processing...")

        thumb = None

        if job.get("thumb_mode") == "saved":
            thumb = get_thumb()

        elif job.get("thumb_mode") == "auto":
            thumb = generate_thumbnail(file_path)

        # ---------------- RENAME ----------------
        if job["mode"] == "rename":
            ext = os.path.splitext(file_path)[1]
            new_path = job["new_name"] + ext
            os.rename(file_path, new_path)
            file_path = new_path

        await status.edit_text("📤 Uploading...")

        caption = f"✅ {job.get('new_name','AniToon File')}"

        if file_path.endswith((".mp4", ".mkv", ".mov")):

            await msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=caption,
                supports_streaming=True
            )

        else:

            await msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=caption
            )

        await status.edit_text("✅ Done")

    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")

    finally:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        remove_user(job["uid"])

# ---------------- RUN ----------------
app.run()
