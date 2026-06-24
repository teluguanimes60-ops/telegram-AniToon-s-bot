from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

flask_app = Flask(__name__)
user_data = {}

# -------- PROGRESS --------
async def progress(current, total, message, start, text):
    diff = time.time() - start
    if diff == 0:
        return

    percent = current * 100 / total
    bar = "█" * int(percent // 10) + "░" * (10 - int(percent // 10))

    try:
        await message.edit_text(
            f"{text}\n\n[{bar}] {percent:.1f}%",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Channel", url="https://t.me/Anitoon_edit/33")]
            ])
        )
    except:
        pass

# -------- BOT --------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------- KEEP ALIVE --------
@flask_app.route("/")
def home():
    return "Bot Running"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()

# -------- BUTTONS --------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🔁 Convert", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

def convert_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 File → Video", callback_data="f2v")],
        [InlineKeyboardButton("🎬 Video → File", callback_data="v2f")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# -------- START --------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🔥 AniToon Bot", reply_markup=main_menu())

# -------- CALLBACK --------
@app.on_callback_query()
async def cb(client, query):
    data = query.data

    if data == "rename":
        await query.message.edit_text("Send file", reply_markup=main_menu())

    elif data == "convert":
        await query.message.edit_text("Choose convert type", reply_markup=convert_menu())

    elif data == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=main_menu())

    elif data == "thumb":
        await query.message.edit_text("Send photo to set thumbnail", reply_markup=main_menu())

    elif data == "back":
        await query.message.edit_text("Main Menu", reply_markup=main_menu())

    elif data in ["f2v", "v2f"]:
        user_data[query.from_user.id] = {"mode": data}
        await query.message.edit_text("Send file to convert")

# -------- FILE RECEIVE --------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["file_msg"] = message

    await message.reply_text("Send new name")

# -------- RENAME / CONVERT --------
@app.on_message(filters.text & ~filters.command(["start"]))
async def process(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    data = user_data[user_id]
    file_msg = data.get("file_msg")
    new_name = message.text

    msg = await message.reply_text("Processing...")

    start_time = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(msg, start_time, "📥 Downloading")
    )

    ext = file_path.split(".")[-1]

    # ✅ FIX: REPLACE NAME (not add)
    new_path = os.path.join(os.path.dirname(file_path), f"{new_name}.{ext}")

    os.rename(file_path, new_path)

    thumb = get_thumb()
    start_time = time.time()

    mode = data.get("mode")

    # -------- CONVERT --------
    if mode == "f2v":
        await message.reply_video(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    elif mode == "v2f":
        await message.reply_document(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    else:
        # NORMAL RENAME
        if file_msg.video:
            await message.reply_video(
                new_path,
                thumb=thumb,
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

# -------- THUMB --------
@app.on_message(filters.photo)
async def thumb(client, message):
    path = await message.download()
    save_thumb(path)
    await message.reply_text("Thumbnail saved")

print("Bot Running...")
app.run()
