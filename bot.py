# =========================
# AniToon Bot - UPGRADED V3
# PART 1/2 - CORE + HANDLERS
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

# ---------------- ENV ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API credentials")

# ---------------- INIT ----------------

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
jobs = {}
last_msg = {}

# ---------------- CLEAN MESSAGES ----------------

async def clean(uid, msg):
    old = last_msg.get(uid)
    if old:
        try:
            await old.delete()
        except:
            pass
    last_msg[uid] = msg

# ---------------- UI BUTTONS ----------------

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
        [InlineKeyboardButton("📌 Saved Thumbnail", callback_data=f"thumb_saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto Thumbnail", callback_data=f"thumb_auto_{job_id}")],
        [InlineKeyboardButton("❌ No Thumbnail", callback_data=f"thumb_none_{job_id}")]
    ])

# ---------------- START ----------------

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

🔥 AniToon Bot
"""

    m = await msg.reply_text(text, reply_markup=main_menu())
    await clean(msg.from_user.id, m)

# ---------------- CALLBACK HANDLER ----------------

@app.on_callback_query()
async def cb(_, q):

    uid = q.from_user.id
    data = q.data

    # BACK
    if data == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        await clean(uid, m)

    # RENAME
    elif data == "rename":
        user_states[uid] = {"mode": "rename", "step": "file"}
        m = await q.message.reply_text("📁 Send file/video", reply_markup=back_btn())
        await clean(uid, m)

    # CONVERT
    elif data == "convert":
        user_states[uid] = {"mode": "convert", "step": "file"}
        m = await q.message.reply_text("🔄 Send file/video", reply_markup=back_btn())
        await clean(uid, m)

    # INSTANT
    elif data == "instant":
        user_states[uid] = {"mode": "instant", "step": "file"}
        m = await q.message.reply_text("⚡ Send file (instant edit)", reply_markup=back_btn())
        await clean(uid, m)

    # THUMB
    elif data == "thumb":
        user_states[uid] = {"mode": "thumb"}
        m = await q.message.reply_text("🖼 Send thumbnail image", reply_markup=back_btn())
        await clean(uid, m)

    # HELP
    elif data == "help":
        await q.message.reply_text("Help system coming...", reply_markup=main_menu())

    # JOB CONTROL
    elif data.startswith("pause_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "pause"
        await q.answer("Paused")

    elif data.startswith("resume_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "run"
        await q.answer("Resumed")

    elif data.startswith("cancel_"):
        job_id = data.split("_")[1]
        if job_id in jobs:
            jobs[job_id]["control"] = "cancel"
        await q.answer("Cancelled")

    # THUMB
    elif data.startswith("thumb_saved_"):
        job_id = data.split("_")[-1]
        jobs[job_id]["thumb"] = "saved"
        await q.message.reply_text("📹 Choose convert type")

    elif data.startswith("thumb_auto_"):
        job_id = data.split("_")[-1]
        jobs[job_id]["thumb"] = "auto"
        await q.message.reply_text("📹 Choose convert type")

    elif data.startswith("thumb_none_"):
        job_id = data.split("_")[-1]
        jobs[job_id]["thumb"] = "none"
        await q.message.reply_text("📹 Choose convert type")

# ---------------- FILE HANDLER ----------------

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # RENAME
    if state["mode"] == "rename":
        state["file"] = msg
        state["step"] = "name"
        m = await msg.reply_text("✏️ Send new name")
        await clean(uid, m)

    # CONVERT
    elif state["mode"] == "convert":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "convert",
            "control": "run",
            "thumb": None,
            "convert_type": None,
            "name": None
        }

        await msg.reply_text("🖼 Choose thumbnail", reply_markup=thumb_buttons(job_id))

    # INSTANT (NO DOWNLOAD FLOW)
    elif state["mode"] == "instant":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "instant",
            "control": "run",
            "thumb": "none",
            "name": None
        }

        state["job_id"] = job_id
        state["step"] = "name"

        await msg.reply_text("⚡ Send new text (instant edit)")

# ---------------- TEXT HANDLER ----------------

@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # RENAME NAME
    if state["mode"] == "rename" and state["step"] == "name":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "mode": "rename",
            "name": msg.text,
            "control": "run",
            "thumb": None
        }

        await msg.reply_text("🖼 Choose thumbnail", reply_markup=thumb_buttons(job_id))
        user_states.pop(uid, None)

    # INSTANT TEXT EDIT (NO DOWNLOAD / NO UPLOAD)
    elif state["mode"] == "instant" and state["step"] == "name":

        job_id = state["job_id"]
        jobs[job_id]["instant_text"] = msg.text

        await msg.reply_text("⚡ Applying instant edit...")

        asyncio.create_task(instant_edit(job_id))
        user_states.pop(uid, None)

# ---------------- INSTANT EDIT ENGINE ----------------

async def instant_edit(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    try:
        msg = job["file"]
        new_text = job.get("instant_text", "")

        await msg.edit_text(new_text)

    except Exception as e:
        print(e)

# =========================
# PART 2/2 - PROCESS ENGINE
# =========================

import os
import time
import asyncio
import subprocess

# ---------------- PROGRESS BAR ----------------

async def progress(current, total, message, start_time):

    try:
        percent = (current * 100) / total if total else 0

        elapsed = time.time() - start_time
        speed = current / (elapsed + 1)

        speed_mb = speed / (1024 * 1024)
        done_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        eta = (total - current) / (speed + 1)

        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = f"""
📥 DOWNLOADING

[{bar}]

📊 {percent:.1f}%

⚡ {speed_mb:.2f} MB/s
📦 {done_mb:.2f} MB / {total_mb:.2f} MB

⏳ ETA: {int(eta)} sec
"""

        await message.edit_text(text, reply_markup=message.reply_markup)

    except:
        pass


# ---------------- UPLOAD PROGRESS ----------------

async def upload_progress(current, total, message, start_time):

    try:
        percent = (current * 100) / total if total else 0

        elapsed = time.time() - start_time
        speed = current / (elapsed + 1)

        speed_mb = speed / (1024 * 1024)

        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))

        text = f"""
📤 UPLOADING

[{bar}]

📊 {percent:.1f}%
⚡ {speed_mb:.2f} MB/s
"""

        await message.edit_text(text, reply_markup=message.reply_markup)

    except:
        pass


# ---------------- MAIN PROCESS ----------------

async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    file_msg = job["file"]

    status = await file_msg.reply_text(
        "📥 Starting download...",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")
            ]
        ])
    )

    start_time = time.time()
    file_path = None

    try:

        # ---------------- DOWNLOAD ----------------
        file_path = await file_msg.download(
            progress=progress,
            progress_args=(status, start_time)
        )

        # ---------------- CHECK CANCEL ----------------
        if job.get("control") == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing...")

        # ---------------- THUMBNAIL ----------------
        thumb = None

        if job.get("thumb") == "saved":
            thumb = get_thumb()

        elif job.get("thumb") == "auto":
            try:
                thumb = generate_thumbnail(file_path)
            except:
                thumb = None

        # ---------------- RENAME ----------------
        if job["mode"] == "rename":

            ext = os.path.splitext(file_path)[1]
            new_path = job["name"] + ext

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
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")
                ],
                [
                    InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")
                ]
            ])
        )

        start_upload = time.time()

        # ---------------- SEND FILE ----------------
        if file_path.lower().endswith((".mp4", ".mkv", ".mov", ".avi")):

            await file_msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('name','file')}",
                progress=upload_progress,
                progress_args=(status, start_upload)
            )

        else:

            await file_msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=f"✅ Done: {job.get('name','file')}",
                progress=upload_progress,
                progress_args=(status, start_upload)
            )

        await status.edit_text("✅ Completed Successfully")

    except Exception as e:
        await status.edit_text(f"❌ Error:\n\n{e}")

    finally:

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        jobs.pop(job_id, None)
