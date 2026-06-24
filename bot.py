from auto_thumb import generate_thumbnail
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
import os, time, asyncio, threading
from flask import Flask

from thumbnail import save_thumb, get_thumb

# ---------------- FLASK ----------------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Alive ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

# ---------------- PROGRESS BAR ----------------
async def progress(current, total, message, start):
    now = time.time()
    diff = now - start
    if diff == 0:
        return

    percent = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0

    bar = "█" * int(percent // 5) + "░" * (20 - int(percent // 5))

    text = f"""
📦 Processing...

[{bar}] {percent:.1f}%

⚡ Speed: {speed/1024/1024:.2f} MB/s
⏳ ETA: {int(eta)} sec
"""

    try:
        await message.edit(text)
    except:
        pass

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("✏️ Edit Caption", callback_data="edit")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")]
    ])

def convert_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 File → Video", callback_data="f2v")],
        [InlineKeyboardButton("🎬 Video → File", callback_data="v2f")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

def process_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🔥 AniToon Bot", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    data = query.data
    user_id = query.from_user.id

    if data == "back":
        await query.message.edit_text("Main Menu", reply_markup=main_menu())

    elif data == "rename":
        user_data[user_id] = {"mode": "rename"}
        await query.message.edit_text("Send file", reply_markup=back_btn())

    elif data == "edit":
        user_data[user_id] = {"mode": "edit"}
        await query.message.edit_text("Send file", reply_markup=back_btn())

    elif data == "convert":
        await query.message.edit_text("Choose convert type", reply_markup=convert_menu())

    elif data == "f2v":
        user_data[user_id] = {"mode": "f2v"}
        await query.message.edit_text("Send file", reply_markup=back_btn())

    elif data == "v2f":
        user_data[user_id] = {"mode": "v2f"}
        await query.message.edit_text("Send video", reply_markup=back_btn())

    elif data == "thumb":
        user_data[user_id] = {"mode": "thumb"}
        await query.message.edit_text("Send photo", reply_markup=back_btn())

# ---------------- FILE RECEIVE ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    mode = user_data[user_id]["mode"]
    user_data[user_id]["file"] = message

    await message.delete()

    if mode in ["rename", "edit"]:
        msg = await client.send_message(message.chat.id, "Send text")
        user_data[user_id]["msg"] = msg

    else:
        await process_file(client, message, user_id)

# ---------------- TEXT ----------------
@app.on_message(filters.text)
async def text_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    data = user_data[user_id]
    file_msg = data.get("file")

    if not file_msg:
        return

    await message.delete()
    await data["msg"].delete()

    if data["mode"] == "rename":
        data["new_name"] = message.text.strip()
        await process_file(client, message, user_id)

    elif data["mode"] == "edit":
        await file_msg.copy(message.chat.id, caption=message.text)
        user_data.pop(user_id)

# ---------------- PROCESS ----------------
async def process_file(client, message, user_id):
    data = user_data[user_id]
    file_msg = data["file"]

    status = await client.send_message(message.chat.id, "⏳ Starting...", reply_markup=process_buttons())

    start = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(status, start)
    )

    thumb = get_thumb()

    if not thumb and file_msg.video:
        thumb = generate_thumbnail(file_path)

    # ---------- RENAME ----------
    if data["mode"] == "rename":
        ext = file_path.split(".")[-1]
        new_path = f"{data['new_name']}.{ext}"
        os.rename(file_path, new_path)
        file_path = new_path

    # ---------- CONVERT ----------
    if data["mode"] == "f2v":
        new_path = file_path + ".mp4"
        os.system(f"ffmpeg -i '{file_path}' '{new_path}'")
        file_path = new_path

    elif data["mode"] == "v2f":
        new_path = file_path.replace(".mp4", ".mkv")
        os.rename(file_path, new_path)
        file_path = new_path

    # ---------- SEND ----------
    await client.send_document(
        message.chat.id,
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
    user_data.pop(user_id)

# ---------------- THUMB ----------------
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    path = await message.download()
    save_thumb(path)
    await message.delete()
    await client.send_message(message.chat.id, "Thumbnail Saved")

print("🚀 Bot Running...")
app.run()
