from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

flask_app = Flask(__name__)
user_data = {}

# ---------- PROGRESS ----------
async def progress(current, total, message, start, text):
    diff = time.time() - start
    if diff == 0:
        return

    percent = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0

    speed_text = f"{speed/1024/1024:.2f} MB/s" if speed > 1024*1024 else f"{speed/1024:.2f} KB/s"
    mins, secs = divmod(int(eta), 60)

    bar = "█" * int(percent // 10) + "░" * (10 - int(percent // 10))

    try:
        await message.edit_text(
            f"{text}\n\n[{bar}] {percent:.1f}%\n⚡ {speed_text}\n⏳ {mins}m {secs}s"
        )
    except:
        pass

# ---------- BOT ----------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------- KEEP ALIVE ----------
@flask_app.route("/")
def home():
    return "Alive"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()

# ---------- BUTTONS ----------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------- START ----------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 **AniToon Bot**\n\nChoose option:",
        reply_markup=main_menu()
    )

# ---------- BUTTONS ----------
@app.on_callback_query()
async def cb(client, query):
    data = query.data
    user_id = query.from_user.id

    # --- MENU ---
    if data == "back":
        await query.message.edit_text("Main Menu", reply_markup=main_menu())

    elif data == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=back_btn())

    elif data == "rename":
        await query.message.edit_text("📁 Send file to rename", reply_markup=back_btn())

    elif data == "thumb":
        await query.message.edit_text("🖼 Send photo to set thumbnail", reply_markup=back_btn())

    # --- FORMAT ---
    elif data in ["mp4", "mkv", "mp3"]:
        if user_id not in user_data:
            return

        file_msg = user_data[user_id]["file_msg"]
        new_name = user_data[user_id]["new_name"]

        msg = await query.message.edit_text("Starting...")

        start_time = time.time()

        file_path = await file_msg.download(
            progress=progress,
            progress_args=(msg, start_time, "📥 Downloading")
        )

        new_path = f"{file_path}.{data}"
        os.rename(file_path, new_path)

        thumb = get_thumb()

        start_time = time.time()

        await query.message.reply_document(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

        os.remove(new_path)
        del user_data[user_id]

        await query.message.reply_text("✅ Done!", reply_markup=main_menu())

# ---------- GET NAME ----------
@app.on_message(filters.text & ~filters.command(["start"]))
async def get_name(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    user_data[user_id]["new_name"] = message.text

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("MP4 🎬", callback_data="mp4"),
            InlineKeyboardButton("MKV 🎥", callback_data="mkv")
        ],
        [InlineKeyboardButton("MP3 🎵", callback_data="mp3")]
    ])

    await message.reply_text("🎯 Choose format:", reply_markup=btn)

# ---------- FILE ----------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id
    user_data[user_id] = {"file_msg": message}

    await message.reply_text("📁 Send new name")

# ---------- THUMB ----------
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    path = await message.download()
    save_thumb(path)
    await message.reply_text("✅ Thumbnail Saved")

print("🚀 Bot Running")
app.run()
