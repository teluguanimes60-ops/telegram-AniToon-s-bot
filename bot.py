from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import threading

app = Client(
    "RenameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is Running 🚀"

# keep alive server (Render requirement)
def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

# /start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Send me a file to rename.")

# file handler
@app.on_message(filters.document | filters.video | filters.audio)
async def rename(client, message):
    file = message.document or message.video or message.audio
    await message.reply_text(
        f"📁 File received:\nName: {file.file_name}\n\nRename feature coming next version 🔧"
    )

print("🚀 Bot is running...")
app.run()
