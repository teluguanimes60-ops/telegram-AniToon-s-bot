# =========================
# AniToon Bot - CLEAN FIXED V3
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
    raise Exception("Missing API credentials")

# ---------------- INIT ----------------

setup_ffmpeg()

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ---------------- FLASK ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running"

threading.Thread(
    target=lambda: web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))),
    daemon=True
).start()

# ---------------- STORAGE ----------------

user_states = {}
jobs = {}
last_msg = {}

# ---------------- CLEAN CHAT ----------------

async def clean(uid, msg=None):
    old = last_msg.get(uid)

    if old:
        try:
            await old.delete()
        except:
            pass

    if msg:
        last_msg[uid] = msg

# ---------------- UI ----------------

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant", callback_data="instant")],
        [InlineKeyboardButton("🖼 Thumb", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ])

def process_btn(job_id):
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

    m = await msg.reply_text(
        "👋 Welcome to AniToon Bot",
        reply_markup=main_menu()
    )

    await clean(msg.from_user.id, m)

# ---------------- CALLBACK ----------------

@app.on_callback_query()
async def cb(_, q):

    uid = q.from_user.id
    d = q.data

    if d == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Menu", reply_markup=main_menu())
        await clean(uid, m)

    elif d == "rename":
        user_states[uid] = {"mode": "rename"}
        m = await q.message.reply_text("📁 Send file or video to rename", reply_markup=back_btn())
        await clean(uid, m)

    elif d == "convert":
        user_states[uid] = {"mode": "convert"}
        m = await q.message.reply_text("🔄 Send file/video to convert", reply_markup=back_btn())
        await clean(uid, m)

    elif d == "instant":
        user_states[uid] = {"mode": "instant"}
        m = await q.message.reply_text("⚡ Send file + new name", reply_markup=back_btn())
        await clean(uid, m)

    elif d == "help":
        m = await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
        await clean(uid, m)

# ---------------- FILE HANDLER ----------------

@app.on_message(filters.document | filters.video)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    if state["mode"] == "rename":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "file": msg,
            "mode": "rename",
            "new_name": None,
            "file_type": "video" if msg.video else "document",
            "control": "run"
        }

        m = await msg.reply_text("✏️ Send new name")
        await clean(uid, m)

        state["job_id"] = job_id

    elif state["mode"] == "convert":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "file": msg,
            "mode": "convert",
            "file_type": "video" if msg.video else "document",
            "control": "run"
        }

        m = await msg.reply_text("🖼 Processing convert...")
        await clean(uid, m)

        asyncio.create_task(process(job_id))

    elif state["mode"] == "instant":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "file": msg,
            "mode": "rename",
            "file_type": "video" if msg.video else "document",
            "control": "run"
        }

        state["job_id"] = job_id

        m = await msg.reply_text("⚡ Send new name instantly")
        await clean(uid, m)

# ---------------- TEXT ----------------

@app.on_message(filters.text & ~filters.command("start"))
async def text(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    job_id = state.get("job_id")
    if not job_id:
        return

    jobs[job_id]["new_name"] = msg.text

    m = await msg.reply_text("⚙️ Processing...")
    await clean(uid, m)

    asyncio.create_task(process(job_id))

    user_states.pop(uid, None)

# ---------------- PROCESS ----------------

async def process(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    msg = job["file"]

    status = await msg.reply_text("📥 Downloading...")

    file_path = await msg.download()

    await status.edit_text("⚙️ Processing...")

    # rename only
    if job["mode"] == "rename":
        ext = os.path.splitext(file_path)[1]
        new_path = job["new_name"] + ext
        os.rename(file_path, new_path)
        file_path = new_path

    await status.edit_text("📤 Uploading...")

    file_type = job["file_type"]

    if file_type == "video":
        await msg.reply_video(video=file_path)
    else:
        await msg.reply_document(document=file_path)

    await status.edit_text("✅ Done")

    try:
        os.remove(file_path)
    except:
        pass

    jobs.pop(job_id, None)

# ---------------- RUN ----------------

app.run()

# =========================
# PART 2/2 - HANDLERS + PROCESS ENGINE
# =========================

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
    await clean_old(msg.from_user.id, m)


# ---------------- CALLBACK HANDLER ----------------
@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    # BACK
    if data == "back":
        user_states[uid] = {}
        m = await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        await clean_old(uid, m)

    # ---------------- RENAME ----------------
    elif data == "rename":
        user_states[uid] = {"mode": "rename", "step": "file"}
        m = await q.message.reply_text("📁 Send file/video to rename", reply_markup=back_btn())
        await clean_old(uid, m)

    # ---------------- CONVERT ----------------
    elif data == "convert":
        user_states[uid] = {"mode": "convert", "step": "file"}
        m = await q.message.reply_text("🔄 Send file/video to convert", reply_markup=back_btn())
        await clean_old(uid, m)

    # ---------------- INSTANT ----------------
    elif data == "instant":
        user_states[uid] = {"mode": "instant", "step": "file"}
        m = await q.message.reply_text("⚡ Send file → then new name", reply_markup=back_btn())
        await clean_old(uid, m)

    # ---------------- THUMB ----------------
    elif data == "thumb":
        user_states[uid] = {"mode": "thumb"}
        m = await q.message.reply_text("🖼 Send thumbnail image", reply_markup=back_btn())
        await clean_old(uid, m)

    # ---------------- HELP ----------------
    elif data == "help":
        m = await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
        await clean_old(uid, m)

    # ---------------- JOB CONTROL ----------------
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

    # ---------------- THUMB ----------------
    elif data.startswith("thumb_saved_"):
        job_id = data.split("_")[-1]
        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "saved"
        await q.message.reply_text("📌 Saved Thumb Selected")

    elif data.startswith("thumb_auto_"):
        job_id = data.split("_")[-1]
        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "auto"
        await q.message.reply_text("⚡ Auto Thumb Selected")

    elif data.startswith("thumb_none_"):
        job_id = data.split("_")[-1]
        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "none"
        await q.message.reply_text("❌ No Thumb Selected")

    # ---------------- CONVERT TYPE ----------------
    elif data.startswith("conv_video_"):
        job_id = data.split("_")[-1]
        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"
        asyncio.create_task(process_job(job_id))
        await q.answer("📹 Video Selected")

    elif data.startswith("conv_file_"):
        job_id = data.split("_")[-1]
        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"
        asyncio.create_task(process_job(job_id))
        await q.answer("📁 File Selected")


# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # ---------------- RENAME ----------------
    if state["mode"] == "rename":

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "rename",
            "new_name": None,
            "control": "run",
            "thumb_mode": None,
            "file_type": "video" if msg.video else "document"
        }

        m = await msg.reply_text("✏️ Send new file name", reply_markup=back_btn())
        await clean_old(uid, m)
        return

    # ---------------- CONVERT ----------------
    if state["mode"] == "convert":

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

        m = await msg.reply_text("🖼 Choose thumbnail type", reply_markup=thumb_buttons(job_id))
        await clean_old(uid, m)
        return

    # ---------------- INSTANT ----------------
    if state["mode"] == "instant":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text("⚡ Send new name instantly", reply_markup=back_btn())
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
            "thumb_mode": None,
            "file_type": "video" if state["file"].video else "document"
        }

        m = await msg.reply_text("🖼 Choose thumbnail", reply_markup=thumb_buttons(job_id))
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
            "thumb_mode": "none",
            "file_type": "video" if state["file"].video else "document"
        }

        await msg.reply_text("⚡ Processing instant edit...")
        asyncio.create_task(process_job(job_id))

        user_states.pop(uid, None)
        return


# ---------------- PROGRESS ----------------
async def progress(current, total, message, start_time):

    try:
        percent = current * 100 / total

        elapsed = time.time() - start_time
        speed = current / (elapsed + 1)

        eta = (total - current) / (speed + 1)

        speed_mb = speed / (1024 * 1024)

        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = f"""
📥 Downloading...

[{bar}]

📊 {percent:.1f}%

⚡ Speed: {speed_mb:.2f} MB/s

⏳ ETA: {int(eta)} sec
"""

        await message.edit_text(text, reply_markup=message.reply_markup)

    except:
        pass


# ---------------- PROCESS ENGINE ----------------
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

        # DOWNLOAD
        file_path = await file_msg.download(
            progress=progress,
            progress_args=(status, start_time)
        )

        # PAUSE
        while job.get("control") == "pause":
            await asyncio.sleep(1)

        if job.get("control") == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        await status.edit_text("⚙️ Processing file...")

        thumb = None

        if job.get("thumb_mode") == "saved":
            thumb = get_thumb()

        elif job.get("thumb_mode") == "auto":
            thumb = generate_thumbnail(file_path)

        # RENAME
        if job["mode"] == "rename":

            ext = os.path.splitext(file_path)[1]
            new_path = job["new_name"] + ext

            os.rename(file_path, new_path)
            file_path = new_path

        # CONVERT
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

        await status.edit_text(
            "📤 Uploading file...",
            reply_markup=process_buttons(job_id)
        )

        # STRICT MEDIA TYPE SEND (FIX YOU WANTED)
        if job.get("file_type") == "video":

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

        await status.edit_text("✅ Completed")

    except Exception as e:
        await status.edit_text(f"❌ Error:\n\n{e}")

    finally:

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        jobs.pop(job_id, None)


# ---------------- RUN BOT ----------------
if __name__ == "__main__":
    print("🚀 AniToon Bot Started")
    app.run()
