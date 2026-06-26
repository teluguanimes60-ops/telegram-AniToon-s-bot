# ==========================================
# AniToon Bot - GOD MODE STABLE FIX
# FULL WORKING VERSION
# ==========================================

import os
import time
import asyncio
import uuid
import subprocess
import threading

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import setup_ffmpeg, generate_thumbnail
from thumbnail import get_thumb

# ---------------- CONFIG ----------------
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

print("🚀 GOD MODE BOT STARTED")

# ---------------- MEMORY ----------------
user_state = {}
jobs = {}

# ---------------- CLEAN UI ----------------
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

def process_menu(job_id):
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
        await q.message.reply_text("⚡ Send file + name instantly")

    elif data == "thumb":
        user_state[uid] = {"mode": "thumb"}
        await q.message.reply_text("🖼 Send thumbnail image")

    # ---------------- THUMB SELECTION ----------------
    elif data.startswith("saved_"):
        job_id = data.split("_")[1]
        jobs[job_id]["thumb"] = "saved"
        await q.answer("Saved thumbnail")

    elif data.startswith("auto_"):
        job_id = data.split("_")[1]
        jobs[job_id]["thumb"] = "auto"
        await q.answer("Auto thumbnail")

    elif data.startswith("none_"):
        job_id = data.split("_")[1]
        jobs[job_id]["thumb"] = None
        await q.answer("No thumbnail")

    # ---------------- JOB CONTROL ----------------
    elif data.startswith("cancel_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["status"] = "cancel"
        await q.answer("Cancelled")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "file": msg,
        "uid": uid,
        "mode": state["mode"],
        "status": "run",
        "thumb": None,
        "name": None
    }

    if state["mode"] == "rename":
        user_state[uid]["file"] = msg
        await msg.reply_text("✏️ Send new name")
        return

    if state["mode"] == "instant":
        user_state[uid]["file"] = msg
        await msg.reply_text("⚡ Send new name instantly")
        return

    await msg.reply_text("🖼 Choose thumbnail", reply_markup=thumb_menu(job_id))

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_state.get(uid)

    if not state:
        return

    # ---------------- RENAME ----------------
    if state["mode"] == "rename":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "file": state["file"],
            "uid": uid,
            "mode": "rename",
            "name": msg.text,
            "status": "run",
            "thumb": None
        }

        asyncio.create_task(process_job(job_id))
        user_state.pop(uid, None)

    # ---------------- INSTANT ----------------
    elif state["mode"] == "instant":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "file": state["file"],
            "uid": uid,
            "mode": "rename",
            "name": msg.text,
            "status": "run",
            "thumb": None
        }

        asyncio.create_task(process_job(job_id))
        user_state.pop(uid, None)

# ---------------- PROCESS ENGINE (FIXED VIDEO MODE) ----------------
async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    msg = job["file"]

    status = await msg.reply_text("📥 Downloading...", reply_markup=process_menu(job_id))

    try:
        file_path = await msg.download()

        if job.get("status") == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing...")

        thumb = None

        if job.get("thumb") == "saved":
            thumb = get_thumb()
        elif job.get("thumb") == "auto":
            thumb = generate_thumbnail(file_path)

        # ---------------- RENAME ----------------
        if job["mode"] == "rename":
            ext = os.path.splitext(file_path)[1]
            new_path = job["name"] + ext
            os.rename(file_path, new_path)
            file_path = new_path

        await status.edit_text("📤 Uploading...")

        caption = f"✅ {job.get('name','AniToon File')}"

        # ---------------- FIX VIDEO SEND ----------------
        if file_path.lower().endswith((".mp4", ".mkv", ".mov")):

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

        jobs.pop(job_id, None)

# ---------------- RUN ----------------
app.run()
