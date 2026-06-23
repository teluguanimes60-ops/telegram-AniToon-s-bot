from pyrogram import Client, filters
from pyrogram.types import ForceReply
from flask import Flask
import os
import threading

API_ID = int(os.getenv("API_ID", "12345"))
API_HASH = os.getenv("API_HASH", "abc")
BOT_TOKEN = os.getenv("BOT_TOKEN", "123:abc")

app = Client(
    "RenameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Rename Bot is Running 🚀"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

user_files = {}

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("👋 Send me a file to rename.")

@app.on_message(filters.document | filters.video | filters.audio)
async def get_file(_, message):
    file = message.document or message.video or message.audio
    user_files[message.from_user.id] = file

    await message.reply_text(
        "✏️ Send new file name (with extension)\nExample: movie.mp4",
        reply_markup=ForceReply(selective=True)
    )

@app.on_message(filters.text & ~filters.command("start"))
async def rename(_, message):
    user_id = message.from_user.id

    if user_id not in user_files:
        return await message.reply_text("⚠️ Send a file first.")

    file = user_files[user_id]
    new_name = message.text.strip()

    await message.reply_text("⬇️ Downloading...")

    path = await app.download_media(file)

    os.makedirs("downloads", exist_ok=True)
    new_path = f"downloads/{new_name}"

    os.rename(path, new_path)

    await message.reply_text("⬆️ Uploading...")

    await app.send_document(
        chat_id=message.chat.id,
        document=new_path,
        caption=f"✅ Renamed to: {new_name}"
    )

    os.remove(new_path)
    user_files.pop(user_id)

print("🚀 Bot Started")
app.run()
