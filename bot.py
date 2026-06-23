from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import threading, os, time

app = Client("probot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot Running 🚀"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

USER_DATA = {}
THUMBNAILS = {}

# START
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="thumb")]
    ])
    await message.reply_text("🔥 PRO MAX Rename Bot\nChoose option:", reply_markup=buttons)

# BUTTON HANDLER
@app.on_callback_query()
async def buttons(client, query):
    data = query.data

    if data == "rename":
        await query.message.edit_text("📤 Send file to rename")

    elif data == "thumb":
        await query.message.edit_text("🖼 Send image to set as thumbnail")

# SET THUMBNAIL
@app.on_message(filters.photo)
async def save_thumb(client, message):
    user_id = message.from_user.id
    path = await message.download()
    THUMBNAILS[user_id] = path
    await message.reply_text("✅ Thumbnail saved!")

# RECEIVE FILE
@app.on_message(filters.document | filters.video | filters.audio)
async def get_file(client, message):
    USER_DATA[message.from_user.id] = message

    size = round(message.document.file_size / (1024*1024), 2) if message.document else "?"
    await message.reply_text(f"📁 File received\nSize: {size} MB\n\n✏️ Send new name")

# RENAME
@app.on_message(filters.text & ~filters.command("start"))
async def rename_file(client, message):
    user_id = message.from_user.id

    if user_id not in USER_DATA:
        return

    old_msg = USER_DATA[user_id]
    new_name = message.text

    file = old_msg.document or old_msg.video or old_msg.audio

    path = await old_msg.download()
    new_path = f"./{new_name}"

    os.rename(path, new_path)

    progress_msg = await message.reply_text("📥 Processing...")

    start_time = time.time()

    thumb = THUMBNAILS.get(user_id, None)

    await client.send_document(
        chat_id=message.chat.id,
        document=new_path,
        thumb=thumb,
        progress=progress,
        progress_args=(progress_msg, start_time)
    )

    os.remove(new_path)
    del USER_DATA[user_id]

# PROGRESS BAR
async def progress(current, total, msg, start):
    percent = current * 100 / total
    speed = current / (time.time() - start + 1)
    bar = "█" * int(percent / 10) + "░" * (10 - int(percent / 10))

    try:
        await msg.edit_text(
            f"📤 Uploading...\n\n"
            f"[{bar}]\n"
            f"{percent:.1f}%\n"
            f"⚡ Speed: {round(speed/1024,2)} KB/s"
        )
    except:
        pass

print("🚀 PRO MAX BOT RUNNING")
app.run()
