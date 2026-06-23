from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import threading

# --- BOT SETUP ---
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- FLASK (KEEP ALIVE) ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is Running 🚀"

@flask_app.route("/ping")
def ping():
    return "Alive 🔥"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

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

# --- BUTTON HANDLER ---
@app.on_callback_query()
async def buttons(client, query):
    data = query.data  # ✅ important fix

    if data == "rename":
        await query.message.edit_text(
            "📁 Send me a file to rename.",
            reply_markup=back_button()
        )

    elif data == "help":
        await query.message.edit_text(
            "ℹ️ How to use:\n\n1. Click Rename\n2. Send file\n3. Get renamed file (next update)",
            reply_markup=back_button()
        )

    elif data == "back":
        await query.message.edit_text(
            "🏠 Main Menu:",
            reply_markup=start_buttons()
        )

# --- FILE HANDLER ---
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    await message.reply_text(
        f"📁 File received: {message.document.file_name if message.document else 'Media'}\n\nRename feature coming soon 🔧"
    )

print("🚀 Bot started...")
app.run()
