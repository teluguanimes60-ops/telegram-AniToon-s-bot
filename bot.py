import os
import time
time.time()
import asyncio
import subprocess
import threading
import uuid
from auto_thumb import generate_thumbnail, setup_ffmpeg, FFMPEG_PATH
from thumbnail import save_thumb, get_thumb
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from auto_thumb import (
    generate_thumbnail,
    setup_ffmpeg,
    FFMPEG_PATH
)

from thumbnail import (
    save_thumb,
    get_thumb
)

from help_text import HELP_TEXT

from buttons import (
    main_menu,
    back_btn,
    process_buttons,
    thumb_buttons,
    convert_buttons
)

# ---------------- ENV ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

setup_ffmpeg()

# ---------------- FLASK ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Alive ✅"

threading.Thread(
    target=lambda: web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    ),
    daemon=True
).start()

# ---------------- BOT ----------------

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- DATABASE ----------------

user_states = {}
jobs = {}
user_last_msg = {}

# ---------------- CLEAN UI ----------------

async def clean_old(uid, msg):
    old = user_last_msg.get(uid)

    if old:
        try:
            await old.delete()
        except:
            pass

    user_last_msg[uid] = msg

# ---------------- JOB CREATE ----------------

def create_job(
    uid,
    file_msg,
    mode="rename"
):
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "uid": uid,
        "file": file_msg,

        "mode": mode,

        "new_name": None,

        "thumb_mode": None,

        "convert_type": None,

        "control": "run",

        "status_msg": None
    }

    return job_id

# ---------------- START ----------------

@app.on_message(filters.command("start"))
async def start(_, msg):

    name = msg.from_user.first_name or "User"

    text = f"""
👋 Hello {name}

📁 Rename Files
🔄 Convert Files
🖼 Thumbnail System
⚡ Instant Edit

━━━━━━━━━━━━━━

🔥 AniToon Rename Bot V2

📢 Powered By:
@AniToon_Edit
"""

    m = await msg.reply_text(
        text,
        reply_markup=main_menu()
    )

    await clean_old(
        msg.from_user.id,
        m
    )

# ---------------- PROGRESS ----------------

async def progress(
    current,
    total,
    status,
    start_time
):
    try:

        percent = current * 100 / total

        speed = current / (
            time.time() - start_time + 1
        )

        eta = (
            total - current
        ) / (speed + 1)

        filled = int(percent / 5)

        bar = (
            "█" * filled
            +
            "░" * (20 - filled)
        )

        text = f"""
📦 Processing

[{bar}]

📊 {percent:.1f}%

⚡ Speed:
{speed/1024:.1f} KB/s

⏳ ETA:
{int(eta)} sec
"""

        await status.edit_text(
            text,
            reply_markup=status.reply_markup
        )

    except:
        pass

# ---------------- CALLBACK ----------------

@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    try:
        await q.message.delete()
    except:
        pass

    # BACK
    if data == "back":

        user_states[uid] = {}

        m = await q.message.reply_text(
            "🔥 Main Menu",
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # RENAME
    elif data == "rename":

        user_states[uid] = {
            "mode": "rename",
            "step": "file"
        }

        m = await q.message.reply_text(
            "📁 Send File To Rename",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # CONVERT
    elif data == "convert":

        user_states[uid] = {
            "mode": "convert",
            "step": "file"
        }

        m = await q.message.reply_text(
            "🔄 Send Video/File To Convert",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # THUMB
    elif data == "thumb":

        user_states[uid] = {
            "mode": "thumb"
        }

        m = await q.message.reply_text(
            "🖼 Send Thumbnail Photo",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # INSTANT EDIT
    elif data == "instant":

        user_states[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send File\n\nAfter Upload I Will Ask New Name Instantly",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # HELP
    elif data == "help":

        m = await q.message.reply_text(
            HELP_TEXT,
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # PAUSE
    elif data.startswith("pause_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "pause"

        await q.answer("⏸ Paused")

    # RESUME
    elif data.startswith("resume_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "run"

        await q.answer("▶ Resumed")

    # CANCEL
    elif data.startswith("cancel_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "cancel"

        await q.answer("❌ Cancelled")

    # THUMB MODES
    elif data.startswith("thumb_saved_"):

        job_id = data.replace("thumb_saved_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "saved"

        await q.answer("📌 Saved Thumbnail Selected")

    elif data.startswith("thumb_auto_"):

        job_id = data.replace("thumb_auto_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "auto"

        await q.answer("⚡ Auto Thumbnail Selected")

    elif data.startswith("thumb_none_"):

        job_id = data.replace("thumb_none_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "none"

        await q.answer("❌ No Thumbnail")

    # CONVERT TYPE
    elif data.startswith("conv_video_"):

        job_id = data.replace("conv_video_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📹 MP4 Selected")

    elif data.startswith("conv_file_"):

        job_id = data.replace("conv_file_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📁 File Selected")

# ---------------- FILE HANDLER ----------------

@app.on_message(
    filters.document |
    filters.video |
    filters.audio
)
async def file_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    # INSTANT EDIT
    if state["mode"] == "instant":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send New Name",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # RENAME
    if state["mode"] == "rename":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send New File Name",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # CONVERT
    if state["mode"] == "convert":

        job_id = create_job(
            uid,
            msg,
            "convert"
        )

        m = await msg.reply_text(
            "🖼 Choose Thumbnail First",
            reply_markup=thumb_buttons(job_id)
        )

        jobs[job_id]["status_msg"] = m

        await clean_old(uid, m)

# ---------------- PHOTO HANDLER ----------------

@app.on_message(filters.photo)
async def thumb_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    if state.get("mode") == "thumb":

        path = await msg.download()

        save_thumb(path)

        m = await msg.reply_text(
            "✅ Thumbnail Saved Successfully"
        )

        await clean_old(uid, m)

# ---------------- CALLBACK ----------------

@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    try:
        await q.message.delete()
    except:
        pass

    # BACK
    if data == "back":

        user_states[uid] = {}

        m = await q.message.reply_text(
            "🔥 Main Menu",
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # RENAME
    elif data == "rename":

        user_states[uid] = {
            "mode": "rename",
            "step": "file"
        }

        m = await q.message.reply_text(
            "📁 Send File To Rename",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # CONVERT
    elif data == "convert":

        user_states[uid] = {
            "mode": "convert",
            "step": "file"
        }

        m = await q.message.reply_text(
            "🔄 Send Video/File To Convert",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # THUMB
    elif data == "thumb":

        user_states[uid] = {
            "mode": "thumb"
        }

        m = await q.message.reply_text(
            "🖼 Send Thumbnail Photo",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # INSTANT EDIT
    elif data == "instant":

        user_states[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send File\n\nAfter Upload I Will Ask New Name Instantly",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # HELP
    elif data == "help":

        m = await q.message.reply_text(
            HELP_TEXT,
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # PAUSE
    elif data.startswith("pause_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "pause"

        await q.answer("⏸ Paused")

    # RESUME
    elif data.startswith("resume_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "run"

        await q.answer("▶ Resumed")

    # CANCEL
    elif data.startswith("cancel_"):

        job_id = data.split("_")[1]

        if job_id in jobs:
            jobs[job_id]["control"] = "cancel"

        await q.answer("❌ Cancelled")

    # THUMB MODES
    elif data.startswith("thumb_saved_"):

        job_id = data.replace("thumb_saved_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "saved"

        await q.answer("📌 Saved Thumbnail Selected")

    elif data.startswith("thumb_auto_"):

        job_id = data.replace("thumb_auto_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "auto"

        await q.answer("⚡ Auto Thumbnail Selected")

    elif data.startswith("thumb_none_"):

        job_id = data.replace("thumb_none_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "none"

        await q.answer("❌ No Thumbnail")

    # CONVERT TYPE
    elif data.startswith("conv_video_"):

        job_id = data.replace("conv_video_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📹 MP4 Selected")

    elif data.startswith("conv_file_"):

        job_id = data.replace("conv_file_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📁 File Selected")

# ---------------- FILE HANDLER ----------------

@app.on_message(
    filters.document |
    filters.video |
    filters.audio
)
async def file_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    # INSTANT EDIT
    if state["mode"] == "instant":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send New Name",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # RENAME
    if state["mode"] == "rename":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send New File Name",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # CONVERT
    if state["mode"] == "convert":

        job_id = create_job(
            uid,
            msg,
            "convert"
        )

        m = await msg.reply_text(
            "🖼 Choose Thumbnail First",
            reply_markup=thumb_buttons(job_id)
        )

        jobs[job_id]["status_msg"] = m

        await clean_old(uid, m)

# ---------------- PHOTO HANDLER ----------------

@app.on_message(filters.photo)
async def thumb_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    if state.get("mode") == "thumb":

        path = await msg.download()

        save_thumb(path)

        m = await msg.reply_text(
            "✅ Thumbnail Saved Successfully"
        )

        await clean_old(uid, m)

# ---------------- START BOT ----------------

if __name__ == "__main__":
    try:
        print("🚀 AniToon Bot Started")
        app.run()
    except Exception as e:
        print(f"❌ BOT ERROR: {e}")
