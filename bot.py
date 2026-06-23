from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
import os, time
from flask import Flask
import threading

app = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ===== Flask keep alive =====
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot Running 🚀"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run).start()

# ===== START =====
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="thumb")]
    ])
    await message.reply_text("👋 Welcome to PRO Rename Bot", reply_markup=buttons)

# ===== BUTTON HANDLER =====
user_data = {}

@app.on_callback_query()
async def buttons(client, query):
    data = query.data

    if data == "rename":
        user_data[query.from_user.id] = {"mode": "rename"}
        await query.message.edit_text("📁 Send file to rename")

    elif data == "thumb":
        user_data[query.from_user.id] = {"mode": "thumb"}
        await query.message.edit_text("🖼 Send photo as thumbnail")

# ===== SAVE THUMB =====
@app.on_message(filters.photo)
async def save_thumb(client, message):
    uid = message.from_user.id
    if user_data.get(uid, {}).get("mode") == "thumb":
        path = f"{uid}_thumb.jpg"
        await message.download(path)
        user_data[uid]["thumb"] = path
        await message.reply_text("✅ Thumbnail saved!")

# ===== FILE HANDLER =====
@app.on_message(filters.document | filters.video | filters.audio)
async def rename_file(client, message):
    uid = message.from_user.id

    if user_data.get(uid, {}).get("mode") != "rename":
        return

    file = message.document or message.video or message.audio

    msg = await message.reply_text("⬇️ Downloading...")

    start = time.time()
    file_path = await message.download()

    await msg.edit_text("✏️ Send new file name")
    user_data[uid]["file"] = file_path
    user_data[uid]["msg"] = msg

# ===== NEW NAME =====
@app.on_message(filters.text & ~filters.command(["start"]))
async def get_name(client, message):
    uid = message.from_user.id

    if uid not in user_data or "file" not in user_data[uid]:
        return

    new_name = message.text
    old_path = user_data[uid]["file"]
    new_path = new_name

    os.rename(old_path, new_path)

    msg = user_data[uid]["msg"]
    await msg.edit_text("⬆️ Uploading...")

    thumb = user_data[uid].get("thumb")

    await message.reply_document(
        new_path,
        thumb=thumb if thumb else None
    )

    os.remove(new_path)

    await msg.delete()
    await message.reply_text("✅ Done!")

# ===== RUN =====
print("🚀 Bot Running...")
app.run()
