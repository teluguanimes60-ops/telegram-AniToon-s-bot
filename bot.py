from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb

flask_app = Flask(__name__)
user_data = {}

# ---------------- PROGRESS BAR ----------------
async def progress(current, total, message, start, text):
    now = time.time()
    diff = now - start

    if diff == 0:
        return

    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0

    # speed format
    if speed > 1024 * 1024:
        speed_text = f"{speed / (1024*1024):.2f} MB/s"
    else:
        speed_text = f"{speed / 1024:.2f} KB/s"

    mins, secs = divmod(int(eta), 60)

    bar = "█" * int(percentage // 10) + "░" * (10 - int(percentage // 10))

    try:
        await message.edit_text(
            f"{text}\n\n"
            f"[{bar}] {percentage:.1f}%\n"
            f"⚡ {speed_text}\n"
            f"⏳ {mins}m {secs}s"
        )
    except:
        pass

# ---------------- BOT ----------------
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- KEEP ALIVE ----------------
@flask_app.route("/")
def home():
    return "Bot Running"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()

# ---------------- UI ----------------
def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Welcome\nChoose option:",
        reply_markup=start_buttons()
    )

# ---------------- GET FILENAME ----------------
@app.on_message(filters.text & ~filters.command(["start"]))
async def get_filename(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    user_data[user_id]["new_name"] = message.text

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("MP4 🎬", callback_data="mp4"),
            InlineKeyboardButton("MKV 🎥", callback_data="mkv")
        ],
        [InlineKeyboardButton("MP3 🎵", callback_data="mp3")]
    ])

    await message.reply_text("Choose format:", reply_markup=buttons)

# ---------------- BUTTON HANDLER ----------------
@app.on_callback_query()
async def buttons(client, query):
    data = query.data
    user_id = query.from_user.id

    # -------- FORMAT --------
    if data in ["mp4", "mkv", "mp3"]:
        if user_id not in user_data:
            return

        file_msg = user_data[user_id]["file_msg"]
        new_name = user_data[user_id]["new_name"]

        msg = await query.message.edit_text("Starting...")

        start_time = time.time()

        # DOWNLOAD
        file_path = await file_msg.download(
            progress=progress,
            progress_args=(msg, start_time, "📥 Downloading")
        )

        new_file = f"{new_name}.{data}"
        new_path = os.path.join(os.path.dirname(file_path), new_file)

        os.rename(file_path, new_path)

        thumb = get_thumb()

        start_time = time.time()

        # UPLOAD
        await query.message.reply_document(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

        os.remove(new_path)
        del user_data[user_id]

        await query.message.reply_text("✅ Done!")

    # -------- MENU --------
    elif data == "rename":
        await query.message.edit_text("📁 Send file")

    elif data == "help":
        await query.message.edit_text("Send file → name → format")

# ---------------- THUMBNAIL ----------------
@app.on_message(filters.photo)
async def set_thumbnail(client, message):
    path = await message.download()
    save_thumb(path)
    await message.reply_text("✅ Thumbnail saved")

# ---------------- FILE RECEIVE ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def get_file(client, message):
    user_id = message.from_user.id

    user_data[user_id] = {"file_msg": message}

    await message.reply_text(
        "📁 File received\nSend new name (no extension)"
    )

print("🚀 Bot started")
app.run()
