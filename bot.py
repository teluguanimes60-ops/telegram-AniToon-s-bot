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

from instant_edit import instant_edit
from help_text import HELP_TEXT

# ---------------- ENV ----------------
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

API_ID = int(API_ID)

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

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
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

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------------- START (FIXED POSITION) ----------------
@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply_text("🔥 AniToon Bot is Alive", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):
    uid = q.from_user.id

    if q.data == "back":
        user_data[uid] = {}
        await q.message.edit_text("🔥 Main Menu", reply_markup=main_menu())

    elif q.data == "rename":
        user_data[uid] = {"mode": "rename", "step": "wait_file"}
        await q.message.edit_text("📁 Send your file to rename", reply_markup=back_menu())

    elif q.data == "convert":
        user_data[uid] = {"mode": "convert", "step": "wait_file"}
        await q.message.edit_text("🔄 Send file/video to convert", reply_markup=back_menu())

    elif q.data == "thumb":
        user_data[uid] = {"mode": "thumb"}
        await q.message.edit_text("🖼 Send image to save thumbnail", reply_markup=back_menu())

    elif q.data == "instant":
        user_data[uid] = {"mode": "instant"}
        await q.message.edit_text("⚡ Reply to file for instant edit", reply_markup=back_menu())

    elif q.data == "help":
        await q.message.edit_text(HELP_TEXT, reply_markup=main_menu())

    elif q.data.startswith("pause_"):
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
        await q.answer("Cancelled ❌")

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):
    uid = msg.from_user.id

    if uid not in user_data:
        return

    state = user_data[uid]

    if state.get("mode") == "thumb":
        return

    if state.get("mode") == "rename" and state.get("step") == "wait_file":
        state["file"] = msg
        state["step"] = "wait_name"
        await msg.reply("✏️ Now send new file name (without extension)")
        return

    if state.get("mode") == "convert":
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": msg,
            "mode": "convert",
            "control": "run"
        }

        await msg.reply("📥 File received", reply_markup=job_buttons(job_id))

        asyncio.create_task(process_job(job_id))
        return

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text)
async def text_handler(_, msg):
    uid = msg.from_user.id

    if uid not in user_data:
        return

    state = user_data[uid]

    if state.get("mode") == "rename" and state.get("step") == "wait_name":
        state["new_name"] = msg.text
        state["step"] = "done"

        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            "uid": uid,
            "file": state["file"],
            "new_name": state["new_name"],
            "mode": "rename",
            "control": "run"
        }

        await msg.reply("⚙️ Processing rename...", reply_markup=job_buttons(job_id))
        asyncio.create_task(process_job(job_id))

# ---------------- JOB PROCESSOR (FIXED) ----------------
async def process_job(job_id):
    job = jobs[job_id]
    msg = job["file"]

    status = await msg.reply("📥 Downloading...", reply_markup=job_buttons(job_id))

    file_path = await msg.download()

    # ---------------- SAFE PAUSE / CANCEL ----------------
    while True:
        if job["control"] == "cancel":
            await status.edit_text("❌ Cancelled")
            return

        if job["control"] == "pause":
            await asyncio.sleep(1)
            continue

        break

    await status.edit_text("⚙️ Processing...", reply_markup=job_buttons(job_id))

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
        subprocess.run([FFMPEG_PATH, "-i", file_path, new_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

# ---------------- THUMB ----------------
@app.on_message(filters.photo)
async def thumb_handler(_, msg):
    if msg.from_user.id in user_data and user_data[msg.from_user.id].get("mode") == "thumb":
        path = await msg.download()
        save_thumb(path)
        await msg.reply("🖼 Thumbnail Saved Successfully ✅")
    else:
        await msg.reply("⚠️ First click Thumbnail button")

print("🚀 Bot Running...")
app.run()
