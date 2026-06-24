from auto_thumb import generate_thumbnail
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
import os
import threading

from thumbnail import save_thumb, get_thumb
from flask import Flask

# ---------------- FLASK (FOR RENDER FREE) ----------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot Running 🚀"

def run():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run).start()

# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename", callback_data="rename")],
        [InlineKeyboardButton("✏️ Edit Caption", callback_data="edit")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

def process_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("▶️ Resume", callback_data="resume")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/Anitoon_edit")
        ]
    ])

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("🔥 AniToon Bot", reply_markup=main_menu())

# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    data = query.data
    user_id = query.from_user.id

    if data == "back":
        await query.message.edit_text("Main Menu", reply_markup=main_menu())

    elif data == "rename":
        user_data[user_id] = {"mode": "rename"}
        await query.message.edit_text("📁 Send file", reply_markup=back_btn())

    elif data == "edit":
        user_data[user_id] = {"mode": "edit"}
        await query.message.edit_text("✏️ Send file to edit caption", reply_markup=back_btn())

    elif data == "thumb":
        user_data[user_id] = {"mode": "thumb"}
        await query.message.edit_text("🖼 Send photo", reply_markup=back_btn())

    elif data == "help":
        await query.message.edit_text(
            "📌 Send file → choose option → done",
            reply_markup=back_btn()
        )

    elif data == "pause":
        user_data.setdefault(user_id, {})["pause"] = True

    elif data == "resume":
        user_data.setdefault(user_id, {})["pause"] = False

    elif data == "cancel":
        user_data.setdefault(user_id, {})["cancel"] = True

# ---------------- FILE RECEIVE ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    mode = user_data[user_id]["mode"]
    user_data[user_id]["file"] = message

    try:
        await message.delete()
    except:
        pass

    if mode == "rename":
        msg = await client.send_message(message.chat.id, "✏️ Send new file name")
        user_data[user_id]["msg"] = msg

    elif mode == "edit":
        msg = await client.send_message(message.chat.id, "✏️ Send new caption")
        user_data[user_id]["msg"] = msg

# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text)
async def text_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    data = user_data[user_id]
    file_msg = data.get("file")

    if not file_msg:
        return

    try:
        await message.delete()
    except:
        pass

    try:
        await data["msg"].delete()
    except:
        pass

    # ---------------- RENAME ----------------
    if data["mode"] == "rename":
        new_name = message.text.strip()

        status = await client.send_message(
            message.chat.id,
            "⏳ Processing...",
            reply_markup=process_buttons()
        )

        file_path = await file_msg.download()

        ext = file_path.split(".")[-1]
        new_path = os.path.join(os.path.dirname(file_path), f"{new_name}.{ext}")

        os.rename(file_path, new_path)

        thumb = get_thumb()

        if not thumb and file_msg.video:
            thumb = generate_thumbnail(new_path)

        if file_msg.video:
            await client.send_video(message.chat.id, new_path, thumb=thumb)
        elif file_msg.audio:
            await client.send_audio(message.chat.id, new_path)
        else:
            await client.send_document(message.chat.id, new_path, thumb=thumb)

        # delete auto thumb
        if thumb and isinstance(thumb, str):
            try:
                if os.path.exists(thumb) and "thumb" not in thumb:
                    os.remove(thumb)
            except:
                pass

        try:
            os.remove(new_path)
        except:
            pass

        await status.delete()

    # ---------------- EDIT CAPTION ----------------
    elif data["mode"] == "edit":
        await file_msg.copy(
            chat_id=message.chat.id,
            caption=message.text
        )

    user_data.pop(user_id, None)

# ---------------- THUMB ----------------
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    path = await message.download()
    save_thumb(path)

    try:
        await message.delete()
    except:
        pass

    await client.send_message(message.chat.id, "✅ Thumbnail Saved")

print("🚀 Bot Running...")
app.run()
