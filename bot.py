from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import threading
import os

app = Client(
    "ProRenameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "🔥 Ultra Pro Bot Running"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

# store user data
users = {}

# START
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 Send me a file to rename (Ultra Pro Mode)"
    )

# RECEIVE FILE
@app.on_message(filters.document | filters.video | filters.audio)
async def file_received(client, message):
    users[message.from_user.id] = {"file": message}

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Rename", callback_data="rename")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])

    await message.reply_text(
        "📁 File received!\nChoose option:",
        reply_markup=buttons
    )

# BUTTON HANDLER
@app.on_callback_query()
async def button_handler(client, query):
    user_id = query.from_user.id

    if query.data == "rename":
        await query.message.edit_text(
            "✏️ Send new file name with extension\nExample: movie.mkv"
        )

    elif query.data == "cancel":
        users.pop(user_id, None)
        await query.message.edit_text("❌ Cancelled")

# RENAME PROCESS
@app.on_message(filters.text)
async def rename_process(client, message):
    user_id = message.from_user.id

    if user_id not in users:
        return

    new_name = message.text
    old_msg = users[user_id]["file"]

    file = old_msg.document or old_msg.video or old_msg.audio

    status = await message.reply_text("⬇️ Downloading...")

    file_path = await old_msg.download()

    await status.edit("✏️ Renaming...")

    new_path = new_name
    os.rename(file_path, new_path)

    await status.edit("⬆️ Uploading...")

    # thumbnail for video
    thumb = None
    if old_msg.video and old_msg.video.thumbs:
        thumb = await old_msg.download(old_msg.video.thumbs[0].file_id)

    await message.reply_document(
        document=new_path,
        caption="✅ Done!",
        thumb=thumb
    )

    await status.edit("✅ Completed")

    os.remove(new_path)
    users.pop(user_id)

print("🚀 Ultra Pro Bot Started")
app.run()
