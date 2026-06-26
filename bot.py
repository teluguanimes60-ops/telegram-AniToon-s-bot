# =========================
# AniToon Bot - GOD CORE
# PART 1/3 - CORE ENGINE
# =========================

import os
import time
import asyncio
import uuid
import threading
import subprocess

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import setup_ffmpeg, generate_thumbnail
from thumbnail import get_thumb
from utils import get_file_type

# ---------------- ENV ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API credentials")

# ---------------- INIT ----------------

setup_ffmpeg()

# ---------------- FLASK SERVER ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot PRO Running ✅"

def run_web():
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT CLIENT ----------------

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ---------------- MEMORY SYSTEM ----------------

user_states = {}
jobs = {}
last_msg = {}

# ---------------- CLEAN MESSAGE SYSTEM ----------------

async def clean_old(uid, msg):
    """
    Delete previous bot message for clean UI
    """

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
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])


def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
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
        [InlineKeyboardButton("📹 Convert Video", callback_data=f"conv_video_{job_id}")],
        [InlineKeyboardButton("📁 Convert File", callback_data=f"conv_file_{job_id}")]
    ])

print("🚀 AniToon Bot CORE LOADED")

# =========================
# AniToon Bot - GOD CORE
# PART 2/3 - HANDLERS FLOW
# =========================

from utils import build_new_name
from jobs import create_job

# ---------------- START COMMAND ----------------

@app.on_message(filters.command("start"))
async def start(_, msg):

    name = msg.from_user.first_name or "User"

    text = f"""
👋 Hello {name}

📁 Rename Files
🔄 Convert Files
⚡ Instant Edit
🖼 Thumbnail System

━━━━━━━━━━━━━━

🚀 AniToon PRO Bot
"""

    m = await msg.reply_text(text, reply_markup=main_menu())
    await clean_old(msg.from_user.id, m)


# ---------------- CALLBACK HANDLER ----------------

@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    # ---------------- BACK ----------------
    if data == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        await clean_old(uid, m)

    # ---------------- RENAME ----------------
    elif data == "rename":
        user_states[uid] = {
            "mode": "rename",
            "step": "file"
        }

        m = await q.message.reply_text(
            "📁 Send file/video to rename",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    # ---------------- CONVERT ----------------
    elif data == "convert":
        user_states[uid] = {
            "mode": "convert",
            "step": "file"
        }

        m = await q.message.reply_text(
            "🔄 Send file/video to convert",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    # ---------------- INSTANT EDIT ----------------
    elif data == "instant":
        user_states[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send file → then name instantly",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    # ---------------- THUMBNAIL ----------------
    elif data == "thumb":
        user_states[uid] = {
            "mode": "thumb"
        }

        m = await q.message.reply_text(
            "🖼 Send thumbnail image",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    # ---------------- HELP ----------------
    elif data == "help":
        m = await q.message.reply_text(
            "🆘 Help Section Coming Soon",
            reply_markup=main_menu()
        )
        await clean_old(uid, m)

    # ---------------- THUMB OPTIONS ----------------
    elif data.startswith("thumb_saved_"):
        job_id = data.split("_")[-1]

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "saved"

        await q.message.reply_text(
            "📹 Choose output type",
            reply_markup=convert_buttons(job_id)
        )

    elif data.startswith("thumb_auto_"):
        job_id = data.split("_")[-1]

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "auto"

        await q.message.reply_text(
            "📹 Choose output type",
            reply_markup=convert_buttons(job_id)
        )

    elif data.startswith("thumb_none_"):
        job_id = data.split("_")[-1]

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "none"

        await q.message.reply_text(
            "📹 Choose output type",
            reply_markup=convert_buttons(job_id)
        )

    # ---------------- CONVERT TYPE ----------------
    elif data.startswith("conv_video_"):
        job_id = data.split("_")[-1]

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"

        asyncio.create_task(process_job(job_id))
        await q.answer("📹 Video selected")

    elif data.startswith("conv_file_"):
        job_id = data.split("_")[-1]

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"

        asyncio.create_task(process_job(job_id))
        await q.answer("📁 File selected")

        # =========================
# AniToon Bot - GOD ENGINE
# PART 3/3 - PROCESS ENGINE
# =========================

import os
import time
import asyncio
import subprocess

from progress import progress
from thumbnail import get_final_thumbnail
from utils import rename_file, convert_to_mp4, safe_delete


# ---------------- PROCESS JOB ----------------

async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    file_msg = job["file_msg"]
    uid = job["user_id"]

    status = await file_msg.reply_text(
        "📥 Starting download...",
        reply_markup=process_buttons(job_id)
    )

    start_time = time.time()
    file_path = None

    try:

        # ---------------- DOWNLOAD ----------------
        file_path = await file_msg.download(
            progress=progress,
            progress_args=(status, start_time)
        )

        job["file_path"] = file_path

        # ---------------- CONTROL CHECK ----------------
        while job.get("status") == "paused":
            await asyncio.sleep(1)

        if job.get("status") == "cancelled":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing file...")

        # ---------------- THUMBNAIL ----------------
        thumb = get_final_thumbnail(
            job.get("thumb_mode"),
            file_path
        )

        # ---------------- RENAME MODE ----------------
        if job["mode"] == "rename":

            new_name = build_new_name(file_path, job["new_name"])
            new_path = rename_file(file_path, new_name)

            file_path = new_path

        # ---------------- CONVERT MODE ----------------
        elif job["mode"] == "convert":

            if job.get("convert_type") == "video":
                file_path = convert_to_mp4(file_path)

        # ---------------- UPLOAD ----------------
        await status.edit_text(
            "📤 Uploading file...",
            reply_markup=process_buttons(job_id)
        )

        # ---------------- SMART SEND ----------------

        ext = os.path.splitext(file_path)[1].lower()

        is_video = ext in [".mp4", ".mkv", ".mov"]

        if is_video:
            await file_msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('new_name', 'file')}",
                supports_streaming=True
            )
        else:
            await file_msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('new_name', 'file')}"
            )

        await status.edit_text("✅ Completed Successfully")

    except Exception as e:
        await status.edit_text(f"❌ Error:\n\n{e}")

    finally:

        # ---------------- CLEANUP ----------------
        try:
            safe_delete(file_path)
        except:
            pass

        jobs.pop(job_id, None)