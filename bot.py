# =========================
# AniToon Bot - FINAL CLEAN VERSION
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
from jobs import jobs, create_job
from states import set_state, get_state, clear_state

# =========================
# ENV
# =========================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API credentials")

# =========================
# INIT
# =========================

setup_ffmpeg()

# =========================
# FLASK KEEP ALIVE
# =========================

web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Running ✅"

def run_web():
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_web, daemon=True).start()

# =========================
# CLIENT
# =========================

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# =========================
# UI BUTTONS
# =========================

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
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])


def process_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶ Resume", callback_data=f"resume_{job_id}")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")],
        [InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit/33")]
    ])


def thumb_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Saved", callback_data=f"thumb_saved_{job_id}")],
        [InlineKeyboardButton("⚡ Auto", callback_data=f"thumb_auto_{job_id}")],
        [InlineKeyboardButton("❌ None", callback_data=f"thumb_none_{job_id}")]
    ])


def convert_buttons(job_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📹 Video", callback_data=f"conv_video_{job_id}")],
        [InlineKeyboardButton("📁 File", callback_data=f"conv_file_{job_id}")]
    ])

# =========================
# START
# =========================

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

    await msg.reply_text(text, reply_markup=main_menu())


# =========================
# CALLBACK HANDLER
# =========================

@app.on_callback_query()
async def callback(_, q):

    uid = q.from_user.id
    data = q.data

    if data == "back":
        clear_state(uid)
        await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
        return

    if data == "rename":
        set_state(uid, mode="rename", step="file")
        await q.message.reply_text("📁 Send file/video to rename", reply_markup=back_btn())
        return

    if data == "convert":
        set_state(uid, mode="convert", step="file")
        await q.message.reply_text("🔄 Send file/video to convert", reply_markup=back_btn())
        return

    if data == "instant":
        set_state(uid, mode="instant", step="file")
        await q.message.reply_text("⚡ Send file then name", reply_markup=back_btn())
        return

    if data == "thumb":
        set_state(uid, mode="thumb")
        await q.message.reply_text("🖼 Send thumbnail image", reply_markup=back_btn())
        return

    if data == "help":
        await q.message.reply_text(HELP_TEXT, reply_markup=main_menu())
        return

    # JOB CONTROL
    if data.startswith("pause_"):
        jobs[data.split("_")[1]]["control"] = "pause"
        await q.answer("⏸ Paused")

    elif data.startswith("resume_"):
        jobs[data.split("_")[1]]["control"] = "run"
        await q.answer("▶ Resumed")

    elif data.startswith("cancel_"):
        jobs[data.split("_")[1]]["control"] = "cancel"
        await q.answer("❌ Cancelled")

    # THUMB
    elif data.startswith("thumb_saved_"):
        jobs[data.split("_")[-1]]["thumb_mode"] = "saved"

    elif data.startswith("thumb_auto_"):
        jobs[data.split("_")[-1]]["thumb_mode"] = "auto"

    elif data.startswith("thumb_none_"):
        jobs[data.split("_")[-1]]["thumb_mode"] = "none"

    # CONVERT
    elif data.startswith("conv_video_"):
        job_id = data.split("_")[-1]
        jobs[job_id]["convert_type"] = "video"
        asyncio.create_task(process_job(job_id))

    elif data.startswith("conv_file_"):
        job_id = data.split("_")[-1]
        jobs[job_id]["convert_type"] = "file"
        asyncio.create_task(process_job(job_id))


# =========================
# FILE HANDLER
# =========================

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):

    uid = msg.from_user.id
    state = get_state(uid)

    if not state:
        return

    if state["mode"] in ["rename", "instant"]:

        set_state(uid, file=msg, step="name")

        await msg.reply_text("✏️ Send new name", reply_markup=back_btn())
        return

    if state["mode"] == "convert":

        job_id = create_job(uid, msg, "convert")

        await msg.reply_text(
            "🖼 Choose thumbnail",
            reply_markup=thumb_buttons(job_id)
        )


# =========================
# TEXT HANDLER
# =========================

@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = get_state(uid)

    if not state:
        return

    if state["mode"] == "rename" and state["step"] == "name":

        job_id = create_job(uid, state["file"], "rename")
        jobs[job_id]["new_name"] = msg.text

        asyncio.create_task(process_job(job_id))
        clear_state(uid)
        return

    if state["mode"] == "instant" and state["step"] == "name":

        job_id = create_job(uid, state["file"], "rename")
        jobs[job_id]["new_name"] = msg.text

        asyncio.create_task(process_job(job_id))
        clear_state(uid)
        return


# =========================
# PROCESS ENGINE
# =========================

async def process_job(job_id):

    job = jobs.get(job_id)
    if not job:
        return

    file_msg = job["file_msg"]

    status = await file_msg.reply_text(
        "📥 Downloading...",
        reply_markup=process_buttons(job_id)
    )

    file_path = await file_msg.download()

    # pause/cancel
    while job.get("control") == "pause":
        await asyncio.sleep(1)

    if job.get("control") == "cancel":
        await status.edit_text("❌ Cancelled")
        return

    # thumbnail
    thumb = None
    if job.get("thumb_mode") == "saved":
        thumb = get_thumb()
    elif job.get("thumb_mode") == "auto":
        thumb = generate_thumbnail(file_path)

    # rename
    if job["mode"] == "rename":
        ext = os.path.splitext(file_path)[1]
        new_path = job["new_name"] + ext
        os.rename(file_path, new_path)
        file_path = new_path

    # convert
    if job["mode"] == "convert" and job.get("convert_type") == "video":
        output = file_path + ".mp4"
        subprocess.run(["ffmpeg", "-y", "-i", file_path, output],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        file_path = output

    await status.edit_text("📤 Uploading...")

    if file_path.lower().endswith((".mp4", ".mkv", ".mov")):
        await file_msg.reply_video(file_path, thumb=thumb)
    else:
        await file_msg.reply_document(file_path, thumb=thumb)

    await status.edit_text("✅ Done")


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
    print("🚀 AniToon Bot Running...")
    app.run()
