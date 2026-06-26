# ==========================================
# AniToon Bot - GOD LEVEL FINAL VERSION
# ==========================================

import os
import time
import uuid
import asyncio
import threading
import subprocess

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import setup_ffmpeg, generate_thumbnail, FFMPEG_PATH
from thumbnail import get_thumb
from jobs import create_job, get_job, pause_job, resume_job, cancel_job
from progress import progress
from utils import rename_file, convert_to_mp4

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
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT ----------------
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ---------------- MEMORY ----------------
user_states = {}
last_msg = {}

# ---------------- CLEAN OLD MSG ----------------
async def clean(uid, msg):
    old = last_msg.get(uid)
    if old:
        try:
            await old.delete()
        except:
            pass
    last_msg[uid] = msg

# ---------------- KEYBOARDS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])


def process_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶ Resume", callback_data=f"resume_{job_id}")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")
        ],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")
        ]
    ])


def thumb_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Saved Thumb", callback_data=f"thumb_saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto Thumb", callback_data=f"thumb_auto_{job_id}")],
        [InlineKeyboardButton("❌ No Thumb", callback_data=f"thumb_none_{job_id}")]
    ])


def convert_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 To Video", callback_data=f"conv_video_{job_id}")],
        [InlineKeyboardButton("📁 To File", callback_data=f"conv_file_{job_id}")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    text = f"""
👋 Hello {msg.from_user.first_name}

📁 Rename Files
🔄 Convert Files
⚡ Instant Edit
🆘 Help Menu
"""

    m = await msg.reply_text(text, reply_markup=main_menu())
    await clean(msg.from_user.id, m)

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):

    uid = q.from_user.id
    data = q.data

    if data == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        await clean(uid, m)

    elif data == "rename":
        user_states[uid] = {"mode": "rename"}
        m = await q.message.reply_text("📁 Send file/video", reply_markup=main_menu())
        await clean(uid, m)

    elif data == "convert":
        user_states[uid] = {"mode": "convert"}
        m = await q.message.reply_text("🔄 Send file/video", reply_markup=main_menu())
        await clean(uid, m)

    elif data == "instant":
        user_states[uid] = {"mode": "instant"}
        m = await q.message.reply_text("⚡ Send file then name", reply_markup=main_menu())
        await clean(uid, m)

    # JOB CONTROLS
    elif data.startswith("pause_"):
        pause_job(data.split("_")[1])
        await q.answer("Paused")

    elif data.startswith("resume_"):
        resume_job(data.split("_")[1])
        await q.answer("Resumed")

    elif data.startswith("cancel_"):
        cancel_job(data.split("_")[1])
        await q.answer("Cancelled")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # RENAME
    if state["mode"] == "rename":

        job_id = create_job(uid, msg, "rename")
        job = get_job(job_id)

        job["file_path"] = await msg.download()

        m = await msg.reply_text(
            "🖼 Choose Thumbnail",
            reply_markup=thumb_buttons(job_id)
        )
        await clean(uid, m)

    # CONVERT
    elif state["mode"] == "convert":

        job_id = create_job(uid, msg, "convert")
        job = get_job(job_id)

        job["file_path"] = await msg.download()

        m = await msg.reply_text(
            "🖼 Choose Thumb + Convert",
            reply_markup=thumb_buttons(job_id)
        )
        await clean(uid, m)

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # RENAME FINAL
    if state["mode"] == "rename" and "file" in state:

        job_id = create_job(uid, state["file"], "rename")
        job = get_job(job_id)

        job["new_name"] = msg.text

        m = await msg.reply_text("⚙️ Processing...", reply_markup=process_buttons(job_id))
        await clean(uid, m)

        asyncio.create_task(process_job(job_id))

        user_states[uid] = {}

# ---------------- PROCESS JOB ----------------
async def process_job(job_id):

    job = get_job(job_id)
    if not job:
        return

    msg = job["file_msg"]

    status = await msg.reply_text("📥 Starting...", reply_markup=process_buttons(job_id))

    start = time.time()

    try:
        file_path = job["file_path"]

        # CHECK CANCEL
        if job["control"] == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing...")

        # RENAME
        if job["mode"] == "rename":
            ext = os.path.splitext(file_path)[1]
            new_path = job["new_name"] + ext
            os.rename(file_path, new_path)
            file_path = new_path

        # CONVERT
        elif job["mode"] == "convert":
            file_path = convert_to_mp4(file_path)

        await status.edit_text("📤 Uploading...", reply_markup=process_buttons(job_id))

        thumb = get_thumb()

        # SMART VIDEO SEND (FIX BLACK COVER ISSUE)
        if file_path.endswith(".mp4"):
            await msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=job.get("new_name", "AniToon File")
            )
        else:
            await msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=job.get("new_name", "AniToon File")
            )

        await status.edit_text("✅ Done")

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")

    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        if job_id in jobs:
            del jobs[job_id]

# ---------------- RUN ----------------
print("🚀 AniToon Bot GOD VERSION STARTED")
app.run()