import os
import time
import asyncio
import subprocess
import threading
import uuid
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import generate_thumbnail, setup_ffmpeg, FFMPEG_PATH
from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

# ---------------- ENV ----------------
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

setup_ffmpeg()

# ---------------- FLASK ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Alive ✅"

threading.Thread(
    target=lambda: web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))),
    daemon=True
).start()

# ---------------- BOT ----------------
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- GLOBAL STORAGE ----------------
user_data = {}
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

# ---------------- BUTTONS ----------------
def main_menu(name="User"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert File", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

def job_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{job_id}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")]
    ])

def thumb_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Saved Thumb", callback_data=f"thumb_saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto Thumb", callback_data=f"thumb_auto_{job_id}")],
        [InlineKeyboardButton("❌ No Thumb", callback_data=f"thumb_none_{job_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    name = msg.from_user.first_name or "User"

    text = f"""
👋 Hello {name} ✨

📁 I am your **AniToon Rename & Convert Bot**

⚡ Rename files instantly  
🔄 Convert Video ↔ File  
🖼 Smart Thumbnail system  
🚀 Fast processing engine  

✨ Click buttons below to continue
🚀 Powered By: @AniToon_Edit
"""

    m = await msg.reply_text(text, reply_markup=main_menu(name))
    await clean_old(msg.from_user.id, m)

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):
    uid = q.from_user.id
    data = q.data

    try:
        await q.message.delete()
    except:
        pass

    # -------- MAIN MENU --------
    if data == "back":
        user_data[uid] = {}
        m = await q.message.reply_text("🔥 Main Menu", reply_markup=main_menu())
        await clean_old(uid, m)

    elif data == "rename":
        user_data[uid] = {"mode": "rename", "step": "file"}
        m = await q.message.reply_text("📁 Send file to rename", reply_markup=back_btn())
        await clean_old(uid, m)

    elif data == "convert":
        user_data[uid] = {"mode": "convert", "step": "file"}
        m = await q.message.reply_text(
            "🔄 Send file/video\nThen choose format",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    elif data == "thumb":
        user_data[uid] = {"mode": "thumb"}
        m = await q.message.reply_text(
            "🖼 Send image to save thumbnail",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    elif data == "instant":
        user_data[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send file first\nThen I will ask rename instantly",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    elif data == "help":
        m = await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
        await clean_old(uid, m)

    # -------- JOB CONTROLS --------
    elif data.startswith("pause_"):
        job_id = data.split("_")[1]
        jobs[job_id]["control"] = "pause"
        await q.answer("Paused ⏸")

    elif data.startswith("resume_"):
        job_id = data.split("_")[1]
        jobs[job_id]["control"] = "run"
        await q.answer("Resumed ▶️")

    elif data.startswith("cancel_"):
        job_id = data.split("_")[1]
        jobs[job_id]["control"] = "cancel"
        await q.answer("Cancelled ❌")

    # -------- THUMB OPTIONS --------
    elif data.startswith("thumb_saved_"):
        job_id = data.split("_")[2]
        jobs[job_id]["thumb_mode"] = "saved"
        await q.answer("Saved Thumb")

    elif data.startswith("thumb_auto_"):
        job_id = data.split("_")[2]
        jobs[job_id]["thumb_mode"] = "auto"
        await q.answer("Auto Thumb")

    elif data.startswith("thumb_none_"):
        job_id = data.split("_")[2]
        jobs[job_id]["thumb_mode"] = "none"
        await q.answer("No Thumb")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):
    uid = msg.from_user.id
    state = user_data.get(uid)

    if not state:
        return

    try:
        await msg.delete()
    except:
        pass

    # ---------------- INSTANT EDIT (STEP 1) ----------------
    if state["mode"] == "instant":
        state["file"] = msg

        m = await msg.reply_text(
            "⚡ File received!\n✏️ Now send NEW NAME instantly",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)
        return

    # ---------------- RENAME (STEP 1) ----------------
    if state["mode"] == "rename":
        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send new name (without extension)",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)
        return

    # ---------------- CONVERT (STEP 1) ----------------
    if state["mode"] == "convert":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "convert",
            "control": "run",
            "thumb_mode": None,
            "convert_type": None
        }

        m = await msg.reply_text(
            "🔄 Choose output format:\n\n📹 Video (MP4)\n📁 File (original)",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📹 Video", callback_data=f"conv_video_{job_id}"),
                    InlineKeyboardButton("📁 File", callback_data=f"conv_file_{job_id}")
                ]
            ])
        )

        await clean_old(uid, m)
        return


# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text)
async def text_handler(_, msg):
    uid = msg.from_user.id
    state = user_data.get(uid)

    if not state:
        return

    try:
        await msg.delete()
    except:
        pass

    # ---------------- INSTANT EDIT (STEP 2) ----------------
    if state["mode"] == "instant" and "file" in state:
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "new_name": msg.text,
            "mode": "rename",
            "control": "run",
            "thumb_mode": None
        }

        m = await msg.reply_text(
            "⚡ Instant rename started...",
            reply_markup=job_buttons(job_id)
        )

        await clean_old(uid, m)

        asyncio.create_task(process_job(job_id))

        # reset state
        user_data[uid] = {}
        return

    # ---------------- NORMAL RENAME (STEP 2) ----------------
    if state["mode"] == "rename" and state.get("step") == "name":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "new_name": msg.text,
            "mode": "rename",
            "control": "run",
            "thumb_mode": None
        }

        m = await msg.reply_text(
            "⚙️ Processing rename...",
            reply_markup=job_buttons(job_id)
        )

        await clean_old(uid, m)

        asyncio.create_task(process_job(job_id))

        # reset state
        user_data[uid] = {}
        return


# ---------------- CONVERT CALLBACK ----------------
@app.on_callback_query()
async def convert_callback(_, q):
    data = q.data

    if data.startswith("conv_video_"):
        job_id = data.split("_")[2]

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"
            asyncio.create_task(process_job(job_id))
            await q.answer("Video mode selected")

    elif data.startswith("conv_file_"):
        job_id = data.split("_")[2]

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"
            asyncio.create_task(process_job(job_id))
            await q.answer("File mode selected")

import time
import os

# ---------------- PROGRESS CALLBACK ----------------
async def progress(current, total, msg, start_time):
    if total == 0:
        return

    job_id = None

    # find job by message
    for j_id, job in jobs.items():
        if job["file"].id == msg.id:
            job_id = j_id
            break

    if not job_id:
        return

    job = jobs.get(job_id)
    if not job:
        return

    # cancel check
    if job["control"] == "cancel":
        return

    # pause check
    while job["control"] == "pause":
        await asyncio.sleep(0.5)

    elapsed = time.time() - start_time
    speed = current / (elapsed + 1)
    percent = (current * 100) / total
    eta = (total - current) / (speed + 1)

    bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))

    text = f"""
📦 Processing...

[{bar}] {percent:.1f}%

⚡ Speed: {speed/1024:.2f} KB/s
⏳ ETA: {int(eta)} sec
"""

    try:
        await msg.edit_text(text, reply_markup=job_buttons(job_id))
    except:
        pass


# ---------------- JOB PROCESSOR ----------------
async def process_job(job_id):
    job = jobs.get(job_id)

    if not job:
        return

    msg = job["file"]

    # ---------------- DOWNLOAD ----------------
    status = await msg.reply_text(
        "📥 Downloading...",
        reply_markup=job_buttons(job_id)
    )

    start_time = time.time()

    file_path = await msg.download(
        progress=progress,
        progress_args=(status, start_time)
    )

    # ---------------- CONTROL CHECK ----------------
    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    while job["control"] == "pause":
        await asyncio.sleep(1)

    await status.edit_text(
        "⚙️ Processing file...",
        reply_markup=job_buttons(job_id)
    )

    # ---------------- THUMBNAIL ----------------
    thumb = None

    if job.get("thumb_mode") == "saved":
        thumb = get_thumb()

    elif job.get("thumb_mode") == "auto":
        thumb = generate_thumbnail(file_path)

    elif job.get("thumb_mode") == "none":
        thumb = None

    else:
        thumb = get_thumb() or generate_thumbnail(file_path)

    # ---------------- RENAME ----------------
    if job["mode"] == "rename":
        ext = file_path.split(".")[-1]
        new_path = file_path.replace(ext, job["new_name"] + "." + ext)
        os.rename(file_path, new_path)
        file_path = new_path

    # ---------------- CONVERT ----------------
    elif job["mode"] == "convert":
        if job.get("convert_type") == "video":
            new_path = file_path + ".mp4"

            subprocess.run(
                [FFMPEG_PATH, "-i", file_path, new_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            file_path = new_path

        # file mode = no conversion (just upload original)

    # ---------------- UPLOAD ----------------
    await status.edit_text(
        "📤 Uploading...",
        reply_markup=job_buttons(job_id)
    )

    await msg.reply_document(file_path, thumb=thumb)

    # ---------------- CLEANUP ----------------
    try:
        os.remove(file_path)
    except:
        pass

    await status.delete()
    jobs.pop(job_id, None)


# ---------------- THUMB HANDLER ----------------
@app.on_message(filters.photo)
async def thumb_handler(_, msg):
    uid = msg.from_user.id

    if uid in user_data and user_data[uid].get("mode") == "thumb":
        path = await msg.download()
        save_thumb(path)

        m = await msg.reply_text("🖼 Thumbnail Saved ✅")
        await clean_old(uid, m)
