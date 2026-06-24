from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
flask_app = Flask(__name__)
user_data = {}
import os
import time
import threading
from thumbnail import save_thumb, get_thumb

async def progress(current, total, message, start, text):
    now = time.time()
    diff = now - start

    if round(diff % 5) == 0:  # update every 5 sec
        percentage = current * 100 / total
        bar = "█" * int(percentage // 10) + "░" * (10 - int(percentage // 10))

        try:
            await message.edit_text(
                f"{text}\n\n[{bar}] {percentage:.1f}%"
            )
        except:
            pass
# --- BOT SETUP ---
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- FLASK (KEEP ALIVE) ---
@flask_app.route("/")
def home():
    return "Bot is Running 🚀"

@flask_app.route("/ping")
def ping():
    return "Alive 🔥"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()

# --- START BUTTON UI ---
def start_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

# --- BACK BUTTON ---
def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# --- START COMMAND ---
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Welcome to AniToon Rename Bot\n\nChoose an option:",
        reply_markup=start_buttons()
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def get_filename(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    user_data[user_id]["new_name"] = message.text

    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("MP4 🎬", callback_data="mp4"),
            InlineKeyboardButton("MKV 🎥", callback_data="mkv")
        ],
        [
            InlineKeyboardButton("MP3 🎵", callback_data="mp3")
        ]
    ])

    await message.reply_text(
        "🎯 Choose format:",
        reply_markup=buttons
    )
    
# --- BUTTON HANDLER ---
@app.on_callback_query()
async def buttons(client, query):
    data = query.data
    user_id = query.from_user.id

    # --- FORMAT SELECT ---
    if data in ["mp4", "mkv", "mp3"]:
        if user_id not in user_data:
            return

        file_msg = user_data[user_id]["file_msg"]
        new_name = user_data[user_id]["new_name"]

        await query.message.edit_text("⏳ Processing...")

        file_path = await file_msg.download()

        import os
        new_file = f"{new_name}.{data}"
        new_path = os.path.join(os.path.dirname(file_path), new_file)

        os.rename(file_path, new_path)

thumb = get_thumb()

await query.message.reply_document(
    new_path,
    thumb=thumb
)

        os.remove(new_path)
        del user_data[user_id]

        await query.message.reply_text("✅ Done!")

    # --- MENU BUTTONS ---
    elif data == "rename":
        await query.message.edit_text("📁 Send file")

    elif data == "help":
        await query.message.edit_text("Send file → enter name → choose format")

    elif data == "back":
        await query.message.edit_text("Main menu")

# --- FILE HANDLER ---
@app.on_message(filters.document | filters.video | filters.audio)
@app.on_message(filters.photo)
async def set_thumbnail(client, message):
    file_path = await message.download()
    save_thumb(file_path)

    await message.reply_text("✅ Thumbnail saved!")
    
async def get_file(client, message):
    user_id = message.from_user.id

    user_data[user_id] = {
        "file_msg": message
    }

    await message.reply_text(
        "📁 File received!\n\nSend new file name (without extension)\nExample: movie"
    )

print("🚀 Bot started...")
app.run()
