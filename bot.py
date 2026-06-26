# ==========================================
# AniToon Bot - STABLE PRO CORE
# PART 1/3
# ==========================================

import os
import time
import asyncio
import threading
import uuid

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import setup_ffmpeg

# ---------------- ENV SAFETY ----------------
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("❌ Missing API_ID / API_HASH / BOT_TOKEN")

API_ID = int(API_ID)

# ---------------- INIT FFmpeg ----------------
setup_ffmpeg()

# ---------------- FLASK SERVER ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# IMPORTANT: single safe thread (NO crashes)
threading.Thread(target=run_web, daemon=True).start()

# ---------------- PYROGRAM CLIENT ----------------
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

print("🚀 AniToon Bot STABLE CORE LOADED")

# ---------------- MEMORY SYSTEM ----------------
user_states = {}
jobs = {}
last_message = {}

# ---------------- SAFE MESSAGE CLEANER ----------------
async def clean_old(uid, msg):
    try:
        old = last_message.get(uid)
        if old:
            await old.delete()
    except:
        pass

    last_message[uid] = msg

# ---------------- KEYBOARDS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

# ==========================================
# AniToon Bot - STABLE PRO CORE
# PART 2/3 - HANDLERS
# ==========================================

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
🔥 AniToon Bot STABLE PRO
"""

    m = await msg.reply_text(text, reply_markup=main_menu())
    await clean_old(msg.from_user.id, m)


# ---------------- CALLBACK HANDLER ----------------
@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    # RESET
    if data == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        await clean_old(uid, m)

    # ---------------- RENAME ----------------
    elif data == "rename":
        user_states[uid] = {"mode": "rename", "step": "file"}

        m = await q.message.reply_text(
            "📁 Send file/video to rename",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)

    # ---------------- CONVERT ----------------
    elif data == "convert":
        user_states[uid] = {"mode": "convert", "step": "file"}

        m = await q.message.reply_text(
            "🔄 Send file/video to convert",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)

    # ---------------- INSTANT ----------------
    elif data == "instant":
        user_states[uid] = {"mode": "instant", "step": "file"}

        m = await q.message.reply_text(
            "⚡ Send file → then new name (fast mode)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)

    # ---------------- THUMB ----------------
    elif data == "thumb":
        user_states[uid] = {"mode": "thumb"}

        m = await q.message.reply_text(
            "🖼 Send thumbnail image",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)

    # ---------------- HELP ----------------
    elif data == "help":
        m = await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
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


# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # ---------------- RENAME ----------------
    if state.get("mode") == "rename":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send new file name",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)
        return

    # ---------------- CONVERT ----------------
    if state.get("mode") == "convert":

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

        m = await msg.reply_text(
            "🖼 Choose thumbnail type",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📌 Saved", callback_data=f"thumb_saved_{job_id}")],
                [InlineKeyboardButton("⚡ Auto", callback_data=f"thumb_auto_{job_id}")],
                [InlineKeyboardButton("❌ None", callback_data=f"thumb_none_{job_id}")]
            ])
        )

        await clean_old(uid, m)
        return

    # ---------------- INSTANT ----------------
    if state.get("mode") == "instant":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "⚡ Send new name instantly",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
        await clean_old(uid, m)


# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # ---------------- RENAME ----------------
    if state["mode"] == "rename" and state["step"] == "name":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "mode": "rename",
            "new_name": msg.text,
            "control": "run",
            "thumb_mode": None
        }

        m = await msg.reply_text(
            "🖼 Choose thumbnail",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📌 Saved", callback_data=f"thumb_saved_{job_id}")],
                [InlineKeyboardButton("⚡ Auto", callback_data=f"thumb_auto_{job_id}")],
                [InlineKeyboardButton("❌ None", callback_data=f"thumb_none_{job_id}")]
            ])
        )

        await clean_old(uid, m)
        user_states.pop(uid, None)
        return

    # ---------------- INSTANT ----------------
    if state["mode"] == "instant" and state["step"] == "name":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "mode": "rename",
            "new_name": msg.text,
            "control": "run",
            "thumb_mode": "none"
        }

        m = await msg.reply_text("⚡ Processing instant edit...")
        await clean_old(uid, m)

        asyncio.create_task(process_job(job_id))

        user_states.pop(uid, None)
        return

# ==========================================
# AniToon Bot - STABLE PRO CORE
# PART 3/3 - PROCESS ENGINE
# ==========================================

import os
import time
import asyncio
import subprocess

# ---------------- PROGRESS BAR ----------------
async def progress(current, total, message, start_time):

    try:
        percent = current * 100 / total
        elapsed = time.time() - start_time

        speed = current / (elapsed + 1)
        eta = (total - current) / (speed + 1)

        def mb(x): return x / (1024 * 1024)

        bar_len = int(percent / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        text = f"""
📥 Downloading...

[{bar}] {percent:.1f}%

⚡ Speed: {mb(speed):.2f} MB/s
📦 {mb(current):.2f} / {mb(total):.2f} MB
⏳ ETA: {int(eta)} sec
"""

        await message.edit_text(text, reply_markup=message.reply_markup)

    except:
        pass


# ---------------- PROCESS JOB ----------------
async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    file_msg = job["file"]

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

        # ---------------- CONTROL CHECK ----------------
        if job.get("control") == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        while job.get("control") == "pause":
            await asyncio.sleep(1)

        await status.edit_text("⚙️ Processing file...")

        thumb = None

        # ---------------- THUMBNAIL LOGIC FIX ----------------
        if job.get("thumb_mode") == "saved":
            thumb = get_thumb()

        elif job.get("thumb_mode") == "auto":
            thumb = generate_thumbnail(file_path)

        elif job.get("thumb_mode") == "none":
            thumb = None

        # ---------------- RENAME ----------------
        if job["mode"] == "rename":

            ext = os.path.splitext(file_path)[1]
            new_path = job["new_name"] + ext

            os.rename(file_path, new_path)
            file_path = new_path

        # ---------------- CONVERT ----------------
        elif job["mode"] == "convert" and job.get("convert_type") == "video":

            output = file_path + "_conv.mp4"

            subprocess.run([
                "ffmpeg", "-y",
                "-i", file_path,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-c:a", "aac",
                output
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            file_path = output

        # ---------------- UPLOAD ----------------
        await status.edit_text(
            "📤 Uploading...",
            reply_markup=process_buttons(job_id)
        )

        caption = f"✅ {job.get('new_name','AniToon File')}"

        # ---------------- SMART SEND FIX ----------------
        if file_path.lower().endswith((".mp4", ".mkv", ".mov")):

            await file_msg.reply_video(
                video=file_path,
                thumb=thumb,
                caption=caption,
                supports_streaming=True
            )

        else:

            await file_msg.reply_document(
                document=file_path,
                thumb=thumb,
                caption=caption
            )

        await status.edit_text("✅ Completed Successfully")

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")

    finally:

        # ---------------- CLEANUP SAFE ----------------
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        jobs.pop(job_id, None)


# ---------------- BUTTON BUILDER (SAFE IMPORT FIX) ----------------
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


# ---------------- RUN BOT ----------------
print("🚀 AniToon Bot STABLE PRO FULL LOADED")

app.run()