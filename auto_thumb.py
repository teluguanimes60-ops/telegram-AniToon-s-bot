import os
import time
import threading
import asyncio

from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from auto_thumb import generate_thumbnail, setup_ffmpeg
from thumbnail import save_thumb, get_thumb

# ---------------- SAFETY ENV CHECK ----------------
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN in environment variables")

API_ID = int(API_ID)

# ---------------- INIT FFMPEG ----------------
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

# ---------------- PROGRESS BAR ----------------
async def progress(current, total, status, start):
    if total == 0:
        return

    now = time.time()
    diff = now - start
    if diff < 1:
        return

    percent = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed else 0

    bar_len = int(percent / 5)
    bar = "█" * bar_len + "░" * (20 - bar_len)

    text = (
        f"📦 Processing...\n\n"
        f"[{bar}] {percent:.1f}%\n"
        f"⚡ {speed/1024/1024:.2f} MB/s\n"
        f"⏳ ETA: {int(eta)} sec"
    )

    try:
        await status.edit_text(text)
    except:
        pass

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")]
    ])

def convert_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 File → Video", callback_data="f2v")],
        [InlineKeyboardButton("🎬 Video → File", callback_data="v2f")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

def process_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("🔥 AniToon Bot", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(_, q):
    uid = q.from_user.id

    if q.data == "back":
        await q.message.edit_text("Main Menu", reply_markup=main_menu())

    elif q.data == "rename":
        user_data[uid] = {"mode": "rename"}
        await q.message.edit_text("Send file", reply_markup=back_btn())

    elif q.data == "convert":
        await q.message.edit_text("Choose type", reply_markup=convert_menu())

    elif q.data == "f2v":
        user_data[uid] = {"mode": "f2v"}
        await q.message.edit_text("Send file", reply_markup=back_btn())

    elif q.data == "v2f":
        user_data[uid] = {"mode": "v2f"}
        await q.message.edit_text("Send video", reply_markup=back_btn())

    elif q.data == "thumb":
        user_data[uid] = {"mode": "thumb"}
        await q.message.edit_text("Send photo", reply_markup=back_btn())

# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(_, msg):
    uid = msg.from_user.id

    if uid not in user_data:
        return

    user_data[uid]["file"] = msg

    try:
        await msg.delete()
    except:
        pass

    if user_data[uid]["mode"] == "rename":
        user_data[uid]["msg"] = await msg.reply("Send new name")
    else:
        await process_file(msg, uid)

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text)
async def text_handler(_, msg):
    uid = msg.from_user.id

    if uid not in user_data:
        return

    data = user_data[uid]

    try:
        await msg.delete()
    except:
        pass

    if data["mode"] == "rename":
        data["new_name"] = msg.text.strip()
        await process_file(msg, uid)

# ---------------- PROCESS FILE ----------------
async def process_file(msg, uid):
    data = user_data[uid]
    file_msg = data["file"]

    status = await msg.reply("⏳ Starting...", reply_markup=process_btn())
    start = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(status, start)
    )

    thumb = get_thumb()
    if not thumb:
        try:
            thumb = generate_thumbnail(file_path)
        except:
            thumb = None

    # ---------------- RENAME ----------------
    if data["mode"] == "rename":
        ext = file_path.split(".")[-1]
        new_path = os.path.join(
            os.path.dirname(file_path),
            f"{data['new_name']}.{ext}"
        )
        os.rename(file_path, new_path)
        file_path = new_path

    # ---------------- CONVERT ----------------
    elif data["mode"] == "f2v":
        new_path = file_path + ".mp4"
        os.system(f'ffmpeg -i "{file_path}" "{new_path}"')
        file_path = new_path

    elif data["mode"] == "v2f":
        new_path = file_path + ".mkv"
        os.rename(file_path, new_path)
        file_path = new_path

    # ---------------- SEND ----------------
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

# ---------------- THUMB HANDLER ----------------
@app.on_message(filters.photo)
async def thumb_handler(_, msg):
    path = await msg.download()
    save_thumb(path)
    await msg.reply("Thumbnail Saved ✅")

print("🚀 Bot Running...")
app.run()
