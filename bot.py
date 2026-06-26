# =========================
# AniToon Bot PRO LEVEL
# bot.py (PART 1/3)
# CORE STABILITY ENGINE
# =========================

import os
import time
import asyncio
import subprocess
import threading
import uuid

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import setup_ffmpeg, generate_thumbnail
from thumbnail import get_thumb
from help_text import HELP_TEXT

# ---------------- ENV ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API credentials")

# ---------------- FFmpeg INIT ----------------

setup_ffmpeg()

# ---------------- FLASK SERVER (KEEP ALIVE) ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Running PRO 🚀"

def run_web():
    web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT CLIENT ----------------

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

print("🚀 AniToon Bot PRO Starting...")

# ---------------- MEMORY SYSTEM ----------------

user_states = {}   # user session states
jobs = {}          # active jobs
user_last_msg = {} # message cleanup tracking

# ---------------- CLEAN MESSAGE SYSTEM ----------------

async def clean_old(uid, msg):
    """
    Deletes previous bot message to keep chat clean
    """

    old = user_last_msg.get(uid)

    if old:
        try:
            await old.delete()
        except:
            pass

    user_last_msg[uid] = msg

# ---------------- UI BUTTONS ----------------

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert File", callback_data="convert")],
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
        [InlineKeyboardButton("📌 Saved Thumbnail", callback_data=f"thumb_saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto Thumbnail", callback_data=f"thumb_auto_{job_id}")],
        [InlineKeyboardButton("❌ No Thumbnail", callback_data=f"thumb_none_{job_id}")]
    ])


def convert_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Convert To Video", callback_data=f"conv_video_{job_id}")],
        [InlineKeyboardButton("📁 Convert To File", callback_data=f"conv_file_{job_id}")]
    ])

# =========================
# bot.py (PART 2/3)
# HANDLERS + USER FLOW
# =========================

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

        m = await q.message.reply_text(
            "🏠 Main Menu",
            reply_markup=main_menu()
        )
        await clean_old(uid, m)


    # ---------------- RENAME MODE ----------------
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


    # ---------------- CONVERT MODE ----------------
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
            "⚡ Send file → then new name",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)


    # ---------------- THUMBNAIL MODE ----------------
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
            HELP_TEXT,
            reply_markup=main_menu()
        )
        await clean_old(uid, m)


    # ---------------- JOB CONTROLS ----------------
    elif data.startswith("pause_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "pause"
        await q.answer("⏸ Paused")


    elif data.startswith("resume_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "run"
        await q.answer("▶ Resumed")


    elif data.startswith("cancel_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "cancel"
        await q.answer("❌ Cancelled")


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
# bot.py (PART 3/3)
# CORE PROCESS ENGINE
# =========================

import os
import time
import asyncio
import subprocess


# ---------------- PROGRESS ----------------

async def progress(current, total, message, start_time):

    try:
        if total == 0:
            return

        percent = (current / total) * 100

        elapsed = time.time() - start_time
        speed = current / (elapsed + 1)

        speed_mb = speed / (1024 * 1024)
        done_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        eta = int((total - current) / (speed + 1))

        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))

        text = f"""
📥 Downloading File

[{bar}]

📊 {percent:.1f}%

⚡ {speed_mb:.2f} MB/s
📦 {done_mb:.2f} / {total_mb:.2f} MB

⏳ ETA: {eta} sec
"""

        await message.edit_text(text, reply_markup=message.reply_markup)

    except:
        pass


# ---------------- FILE HANDLER ----------------

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    mode = state.get("mode")


    # ---------------- RENAME ----------------
    if mode == "rename":

        state["file"] = msg
        state["step"] = "name"

        await msg.reply_text(
            "✏️ Send new file name",
            reply_markup=back_btn()
        )
        return


    # ---------------- CONVERT ----------------
    if mode == "convert":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "convert",
            "control": "run",
            "thumb_mode": None,
            "convert_type": None,
            "new_name": None
        }

        await msg.reply_text(
            "🖼 Choose thumbnail type",
            reply_markup=thumb_buttons(job_id)
        )
        return


    # ---------------- INSTANT EDIT ----------------
    if mode == "instant":

        state["file"] = msg
        state["step"] = "name"

        await msg.reply_text(
            "⚡ Send new name instantly",
            reply_markup=back_btn()
        )


# ---------------- TEXT HANDLER ----------------

@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    mode = state.get("mode")


    # ---------------- RENAME FINAL ----------------
    if mode == "rename" and state.get("step") == "name":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "mode": "rename",
            "new_name": msg.text,
            "control": "run",
            "thumb_mode": None
        }

        await msg.reply_text(
            "🖼 Choose thumbnail",
            reply_markup=thumb_buttons(job_id)
        )

        user_states.pop(uid, None)
        return


    # ---------------- INSTANT EDIT FINAL ----------------
    if mode == "instant" and state.get("step") == "name":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "mode": "rename",
            "new_name": msg.text,
            "control": "run",
            "thumb_mode": "none"
        }

        await msg.reply_text("⚡ Instant processing started...")

        asyncio.create_task(process_job(job_id))

        user_states.pop(uid, None)
        return


# ---------------- MAIN PROCESS ENGINE ----------------

async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    file_msg = job["file"]

    status = await file_msg.reply_text(
        "📥 Downloading...",
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

        # ---------------- CONTROL CHECK ----------------
        while job.get("control") == "pause":
            await asyncio.sleep(1)

        if job.get("control") == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing...")

        thumb = None

        # ---------------- THUMBNAIL ----------------
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

        # ---------------- CONVERT ----------------
        elif job["mode"] == "convert":

            if job.get("convert_type") == "video":

                output = file_path + ".mp4"

                subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-i",
                    file_path,
                    output
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                file_path = output

        # ---------------- UPLOAD ----------------
        await status.edit_text(
            "📤 Uploading...",
            reply_markup=process_buttons(job_id)
        )

        # SMART SEND (VIDEO vs DOCUMENT FIX)
        if file_path.lower().endswith((".mp4", ".mkv", ".mov")):

            await file_msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('new_name','file')}"
            )

        else:

            await file_msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('new_name','file')}"
            )

        await status.edit_text("✅ Completed Successfully 🚀")

    except Exception as e:

        await status.edit_text(f"❌ Error:\n\n{e}")

    finally:

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        jobs.pop(job_id, None)