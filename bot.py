from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN
from flask import Flask
import threading

# ---------------- BOT ----------------
app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- FLASK KEEP ALIVE ----------------
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot is alive 🚀"

def run_flask():
    server.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()

# ---------------- HANDLERS ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Bot is running on Render!")

@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    file = message.document or message.video or message.audio
    name = file.file_name if file else "unknown"

    await message.reply_text(
        f"📁 File received!\n\nName: {name}\n\n✅ Bot is working fine on Render"
    )

print("🚀 Bot Started")
app.run()
