import os
import time
import asyncio
import subprocess
import threading
from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import generate_thumbnail, setup_ffmpeg, FFMPEG_PATH
from thumbnail import save_thumb, get_thumb

from instant_edit import instant_edit
from help_text import HELP_TEXT

# ---------------- ENV ----------------
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

API_ID = int(API_ID)

# ---------------- FFMPEG ----------------
setup_ffmpeg()

# ---------------- FLASK ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Alive ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}
jobs = {}
message_tracker = {}

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def process_buttons(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{uid}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{uid}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{uid}")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")]
    ])

# ---------------- CONTROL ----------------
def is_cancel(uid): return control.get(uid) == "cancel"
def is_pause(uid): return control.get(uid) == "pause"

# ---------------- PROGRESS ----------------
async def progress(current, total, status, start):
    if total == 0:
        return

    uid = status.chat.id

    if is_cancel(uid):
        return

    while is_pause(uid):
        await asyncio.sleep(1)

    now = time.time()
    diff = now - start
    if diff < 1:
        return

    percent = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed else 0

    bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))

    text = f"""📦 Processing...

[{bar}] {percent:.1f}%
⚡ {speed/1024/1024:.2f} MB/s
⏳ ETA: {int(eta)} sec
"""

    try:
        await status.edit_text(text, reply_markup=process_buttons(uid))
    except:
        pass

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply_text("🔥 AniToon Bot Ready", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):
    uid = q.from_user.id

    if q.data == "rename":
        user_data[uid] = {"mode": "rename"}
        await q.message.edit_text("📁 Send file for rename")

    elif q.data == "convert":
        user_data[uid] = {"mode": "convert"}
        await q.message.edit_text("🔄 Send file for convert")

    elif q.data == "instant":
        user_data[uid] = {"mode": "instant"}
        await q.message.edit_text("⚡ Reply to file for instant edit")

    elif q.data == "help":
        await q.message.edit_text(HELP_TEXT, reply_markup=main_menu())

    if q.data.startswith("pause_"):
        job_id = q.data.split("_")[1]
        jobs[job_id]["control"] = "pause"
        await q.answer("Paused ⏸")

    elif q.data.startswith("resume_"):
        job_id = q.data.split("_")[1]
        jobs[job_id]["control"] = "run"
        await q.answer("Resumed ▶️")

    elif q.data.startswith("cancel_"):
        job_id = q.data.split("_")[1]
        jobs[job_id]["control"] = "cancel"
        await q.message.edit_text("❌ Cancelled")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):
    uid = msg.from_user.id

    if uid not in user_data:
        return

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "uid": uid,
        "file": msg,
        "mode": user_data[uid]["mode"],
        "control": "run"
    }

    status = await msg.reply(
        f"📥 File received\n🆔 Job ID: {job_id}",
        reply_markup=job_buttons(uid, job_id)
    )

    message_tracker[job_id] = status

    await process_file(job_id)

# ---------------- PROCESS FILE ----------------
async def process_file(job_id):
    job = jobs[job_id]
    msg = job["file"]
    uid = job["uid"]

    status = await msg.reply("📥 Downloading...", reply_markup=job_buttons(uid, job_id))
    start = time.time()

    file_path = await msg.download()

    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    await status.edit_text("⚙️ Processing...", reply_markup=job_buttons(uid, job_id))

    thumb = generate_thumbnail(file_path) or get_thumb()

    if job["mode"] == "convert":
        new_path = file_path + ".mp4"
        subprocess.run([FFMPEG_PATH, "-i", file_path, new_path])
        file_path = new_path

    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    await status.edit_text("📤 Uploading...", reply_markup=job_buttons(uid, job_id))

    await msg.reply_document(file_path, thumb=thumb)

    try:
        os.remove(file_path)
    except:
        pass

    await status.delete()
    jobs.pop(job_id, None)

    # ---------------- CONVERT ----------------
    if data["mode"] == "convert":
        new_path = file_path + ".mp4"
        subprocess.run([FFMPEG_PATH, "-i", file_path, new_path])
        file_path = new_path

    # ---------------- UPLOAD ----------------
    if is_cancel(uid):
        await status.edit_text("❌ Cancelled")
        return

    await status.edit_text("📤 Uploading...", reply_markup=process_buttons(uid))

    await msg.reply_document(
        file_path,
        thumb=thumb,
        progress=progress,
        progress_args=(status, start)
    )

    try:
        os.remove(file_path)
    except:
        pass

    await status.delete()
    user_data.pop(uid, None)

# ---------------- THUMB ----------------
@app.on_message(filters.photo)
async def thumb_handler(_, msg):
    path = await msg.download()
    save_thumb(path)
    await msg.reply("Thumbnail Saved ✅")

print("🚀 Bot Running...")
app.run()
