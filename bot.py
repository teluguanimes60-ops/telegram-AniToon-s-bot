import os
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
user_last_msg = {}
# ---------------- ENV ----------------
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

setup_ffmpeg()

async def clean_old(uid, msg):
    old = user_last_msg.get(uid)
    if old:
        try:
            await old.delete()
        except:
            pass
    user_last_msg[uid] = msg
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
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}
jobs = {}
user_last_msg = {}
last_msg = {}

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

    if data == "back":
        user_data[uid] = {}
        m = await q.message.reply_text("🔥 Main Menu", reply_markup=main_menu())
        await clean_old(uid, m)

    elif data == "rename":
        user_data[uid] = {"mode": "rename", "step": "file"}
        m = await q.message.reply_text("📁 Send file to rename", reply_markup=back_btn())
        await clean_old(uid, m)

    elif data == "convert":
        user_data[uid] = {
            "mode": "convert",
            "step": "file"
        }

        m = await q.message.reply_text(
            "🔄 Send file/video\n\nThen choose output format",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    elif data == "thumb":
        user_data[uid] = {"mode": "thumb"}
        m = await q.message.reply_text("🖼 Send image to save thumbnail", reply_markup=back_btn())
        await clean_old(uid, m)

    elif data == "instant":
        user_data[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send file now\n\n✏️ After sending, I will ask rename instantly",
            reply_markup=back_btn()
        )
        await clean_old(uid, m)

    elif data == "help":
        m = await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
        await clean_old(uid, m)

    elif data.startswith("pause_"):
        jobs[data.split("_")[1]]["control"] = "pause"
        await q.answer("Paused ⏸")

    elif data.startswith("resume_"):
        jobs[data.split("_")[1]]["control"] = "run"
        await q.answer("Resumed ▶️")

    elif data.startswith("cancel_"):
        jobs[data.split("_")[1]]["control"] = "cancel"
        await q.answer("Cancelled ❌")

    elif data.startswith("thumb_saved_"):
        jobs[data.split("_")[2]]["thumb_mode"] = "saved"
        await q.answer("Saved Thumb")

    elif data.startswith("thumb_auto_"):
        jobs[data.split("_")[2]]["thumb_mode"] = "auto"
        await q.answer("Auto Thumb")

    elif data.startswith("thumb_none_"):
        jobs[data.split("_")[2]]["thumb_mode"] = "none"
        await q.answer("No Thumb")
        
    elif data.startswith("conv_video_"):
        job_id = data.split("_")[2]
        jobs[job_id]["convert_type"] = "video"
        asyncio.create_task(process_job(job_id))
        await q.answer("Video selected")

    elif data.startswith("conv_file_"):
        job_id = data.split("_")[2]
        jobs[job_id]["convert_type"] = "file"
        asyncio.create_task(process_job(job_id))
        await q.answer("File selected")

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

    # ---------------- INSTANT EDIT ----------------
if state["mode"] == "instant":
    state["file"] = msg

    m = await msg.reply(
        "✏️ Now send new name instantly (no extra steps)",
        reply_markup=back_btn()
    )

    await clean_old(uid, m)
    return
    
    # ---------------- RENAME ----------------
    if state["mode"] == "rename":
        state["file"] = msg
        state["step"] = "name"
        m = await msg.reply("✏️ Send new name (without extension)", reply_markup=back_btn())
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
        "convert_type": None
    }

    m = await msg.reply(
        "Choose output type:\n\n📹 Video MP4\n📁 File (keep original)",
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

    # ---------------- INSTANT EDIT ----------------
if state["mode"] == "instant":
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "uid": uid,
        "file": state["file"],
        "new_name": msg.text,
        "mode": "rename",
        "control": "run",
        "thumb_mode": None
    }

    m = await msg.reply("⚡ Instant editing started...", reply_markup=job_buttons(job_id))

    await clean_old(uid, m)

    asyncio.create_task(process_job(job_id))
    return
    
    # ---------------- RENAME ----------------
    if state["mode"] == "rename" and state["step"] == "name":
        state["new_name"] = msg.text
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "new_name": msg.text,
            "mode": "rename",
            "control": "run",
            "thumb_mode": None
        }

        m = await msg.reply("⚙️ Processing rename...", reply_markup=job_buttons(job_id))
        await clean_old(uid, m)

        asyncio.create_task(process_job(job_id))
        return
# ---------------- PROGRESS ----------------
async def progress(current, total, msg, start):
    if total == 0:
        return

    percent = current * 100 / total
    speed = current / (time.time() - start + 1)

    eta = (total - current) / (speed + 1)

    bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))

    text = f"""
📦 Processing...

[{bar}] {percent:.1f}%

⚡ Speed: {speed/1024:.1f} KB/s
⏳ ETA: {int(eta)} sec
"""

    try:
        await msg.edit_text(text, reply_markup=None)
    except:
        pass

# ---------------- JOB PROCESSOR ----------------
async def process_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return

    msg = job["file"]

    status = await msg.reply("📥 Downloading...", reply_markup=job_buttons(job_id))

    start_time = time.time()

    file_path = await msg.download(
        progress=progress,
        progress_args=(status, start_time)
    )

    while job["control"] == "pause":
        await asyncio.sleep(1)

    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    await status.edit_text("⚙️ Processing...", reply_markup=job_buttons(job_id))

    thumb = get_thumb() or generate_thumbnail(file_path)

    if job["mode"] == "rename":
        ext = file_path.split(".")[-1]
        new_path = file_path.replace(ext, job["new_name"] + "." + ext)
        os.rename(file_path, new_path)
        file_path = new_path

    elif job["mode"] == "convert":
        new_path = file_path + ".mp4"

        subprocess.run(
            [FFMPEG_PATH, "-i", file_path, new_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        file_path = new_path

    await status.edit_text("📤 Uploading...", reply_markup=job_buttons(job_id))

    await msg.reply_document(file_path, thumb=thumb)

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

        m = await msg.reply("🖼 Thumbnail Saved ✅")
        await clean_old(uid, m)

print("🚀 Bot Running...")
app.run()
