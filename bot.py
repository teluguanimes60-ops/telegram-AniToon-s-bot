from instant_edit import instant_edit
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

flask_app = Flask(__name__)
user_data = {}

# ---------------- PROGRESS ----------------
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

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- KEEP ALIVE ----------------
@flask_app.route("/")
def home():
    return "Bot Running"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()

# ---------------- BUTTONS ----------------
def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])
    
def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 **AniToon Bot**\n\nChoose an option:",
        reply_markup=main_menu()
    )

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    data = query.data

    elif data == "instant":
    await query.message.edit_text(
        "⚡ Send file and reply with /instant"
    )
    
    if data == "back":
        await query.message.edit_text("Main Menu", reply_markup=main_menu())

    elif data == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=back_btn())

    elif data == "rename":
        await query.message.edit_text("📁 Send file to rename", reply_markup=back_btn())

    elif data == "thumb":
        await query.message.edit_text("🖼 Send photo to set thumbnail", reply_markup=back_btn())

# ---------------- FILE RECEIVE ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    user_data[user_id] = {
        "file_msg": message
    }

    await message.reply_text("📁 Send new file name (without extension)")

# ---------------- RENAME LOGIC ----------------
@app.on_message(filters.text & ~filters.command(["start"]))
async def rename_file(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    file_msg = user_data[user_id]["file_msg"]
    new_name = message.text

    msg = await message.reply_text("⏳ Processing...")

    start_time = time.time()

    # DOWNLOAD
    file_path = await file_msg.download(
        progress=progress,
        progress_args=(msg, start_time, "📥 Downloading")
    )

    # KEEP ORIGINAL EXTENSION
    ext = file_path.split(".")[-1]
    new_path = f"{os.path.splitext(file_path)[0]}_{new_name}.{ext}"

    os.rename(file_path, new_path)

    thumb = get_thumb()
    start_time = time.time()

    # AUTO SEND TYPE
    if file_msg.video:
        await message.reply_video(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    elif file_msg.audio:
        await message.reply_audio(
            new_path,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    else:
        await message.reply_document(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    os.remove(new_path)
    del user_data[user_id]

    await message.reply_text("✅ Done!", reply_markup=main_menu())

# ---------------- THUMBNAIL ----------------
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    path = await message.download()
    save_thumb(path)
    await message.reply_text("✅ Thumbnail Saved")

@app.on_message(filters.command("instant"))
async def instant_cmd(client, message):
    await instant_edit(client, message)

print("🚀 Bot Running...")
app.run()
