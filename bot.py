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
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}
jobs = {}
user_messages = {}   # track last bot msg per user

# ---------------- CLEAN MSG TRACK ----------------
last_bot_msg = {}

async def safe_edit(msg, text, reply_markup=None):
    try:
        return await msg.edit_text(text, reply_markup=reply_markup)
    except:
        return None

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])

def job_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{job_id}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")]
    ])

async def clean_old(uid, msg):
    try:
        old = user_messages.get(uid)
        if old:
            await old.delete()
    except:
        pass

    user_messages[uid] = msg
# ---------------- PROGRESS BAR ----------------
async def progress(current, total, msg, start):
    if total == 0:
        return

    job_id = msg.chat.id

    job = jobs.get(job_id)
    if not job:
        return

    if job["control"] == "cancel":
        return

    while job["control"] == "pause":
        await asyncio.sleep(1)

    percent = current * 100 / total
    bar = "█" * int(percent // 5) + "░" * (20 - int(percent // 5))

    text = (
        f"📦 Processing...\n\n"
        f"[{bar}] {percent:.1f}%\n"
        f"⚡ {current/1024/1024:.2f} MB\n"
    )

    try:
        await msg.edit_text(text, reply_markup=job_buttons(job_id))
    except:
        pass

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):
    uid = q.from_user.id

    # delete old UI for clean look
    try:
        await q.message.delete()
    except:
        pass

    if q.data == "back":
        user_data[uid] = {}
        m = await q.message.reply_text("🔥 Main Menu", reply_markup=main_menu())
        last_bot_msg[uid] = m

    elif q.data == "rename":
        user_data[uid] = {"mode": "rename", "step": "file"}
        await q.message.reply_text("📁 Send file for rename", reply_markup=back_btn())

    elif q.data == "convert":
        user_data[uid] = {"mode": "convert", "step": "file"}
        await q.message.reply_text("🔄 Send file to convert", reply_markup=back_btn())

    elif q.data == "thumb":
        user_data[uid] = {"mode": "thumb"}
        await q.message.reply_text("🖼 Send thumbnail image", reply_markup=back_btn())

    elif q.data == "instant":
        user_data[uid] = {"mode": "instant"}
        await q.message.reply_text("⚡ Send file for instant edit", reply_markup=back_btn())

    elif q.data == "help":
        await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())

    elif q.data.startswith("pause_"):
        jobs[q.data.split("_")[1]]["control"] = "pause"
        await q.answer("Paused")

    elif q.data.startswith("resume_"):
        jobs[q.data.split("_")[1]]["control"] = "run"
        await q.answer("Resumed")

    elif q.data.startswith("cancel_"):
        jobs[q.data.split("_")[1]]["control"] = "cancel"
        await q.answer("Cancelled")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):
    uid = msg.from_user.id
    state = user_data.get(uid)

    if not state:
        return

    # delete user message for clean UI
    try:
        await msg.delete()
    except:
        pass

    if state["mode"] == "rename":
        state["file"] = msg
        state["step"] = "name"
        m = await msg.reply("✏️ Send new file name (without extension)")
        last_bot_msg[uid] = m
        return

    if state["mode"] == "convert":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "convert",
            "control": "run",
            "thumb_mode": None
        }

        m = await msg.reply("📥 File received. Choose output:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Video", callback_data=f"out_video_{job_id}")],
                [InlineKeyboardButton("📁 File", callback_data=f"out_file_{job_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )

        last_bot_msg[uid] = m

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    m = await msg.reply_text("🔥 AniToon's Rename Bot", reply_markup=main_menu())
    await clean_old(msg.from_user.id, m)

    if not state:
        return

    try:
        await msg.delete()
    except:
        pass

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

        await msg.reply("⚙️ Processing...", reply_markup=job_buttons(job_id))
        asyncio.create_task(process_job(job_id))

# ---------------- THUMB SELECT ----------------
async def ask_thumb(job_id, msg):
    return await msg.reply(
        "🖼 Choose Thumbnail:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Saved Thumb", callback_data=f"thumb_saved_{job_id}")],
            [InlineKeyboardButton("⚡ Auto Thumb", callback_data=f"thumb_auto_{job_id}")],
            [InlineKeyboardButton("❌ No Thumb", callback_data=f"thumb_none_{job_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ])
    )

# ---------------- JOB PROCESSOR ----------------
async def process_job(job_id):
    job = jobs[job_id]
    msg = job["file"]

    status = await msg.reply("📥 Downloading...", reply_markup=job_buttons(job_id))

    file_path = await msg.download()

    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    # ask thumbnail choice BEFORE processing
    thumb = get_thumb()

    if not thumb:
        try:
            thumb = generate_thumbnail(file_path)
        except:
            thumb = None

    if job["mode"] == "rename":
        ext = file_path.split(".")[-1]
        new_path = os.path.join(os.path.dirname(file_path), f"{job['new_name']}.{ext}")
        os.rename(file_path, new_path)
        file_path = new_path

    elif job["mode"] == "convert":
        new_path = file_path + ".mp4"
        subprocess.run([FFMPEG_PATH, "-i", file_path, new_path])
        file_path = new_path

    if job["control"] == "cancel":
        await status.edit_text("❌ Cancelled")
        return

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
        await msg.reply("🖼 Thumbnail Saved ✅")
    else:
        await msg.reply("⚠️ Click Thumbnail first")

print("🚀 Bot Running...")
app.run()
