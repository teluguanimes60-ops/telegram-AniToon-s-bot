from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN
import os, time

from thumbnail import save_thumb, get_thumb

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
        await query.message.edit_text("Send file → rename / edit caption / thumbnail", reply_markup=back_btn())

    elif data == "pause":
        user_data[user_id]["pause"] = True

    elif data == "resume":
        user_data[user_id]["pause"] = False

    elif data == "cancel":
        user_data[user_id]["cancel"] = True

# ---------------- FILE RECEIVE ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    mode = user_data[user_id]["mode"]
    user_data[user_id]["file"] = message

    # delete old message (clean UI)
    try:
        await message.delete()
    except:
        pass

    if mode == "rename":
        msg = await message.reply_text("✏️ Send new file name")
        user_data[user_id]["msg"] = msg

    elif mode == "edit":
        msg = await message.reply_text("✏️ Send new caption")
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

    # delete user text (clean chat)
    try:
        await message.delete()
    except:
        pass

    # delete previous bot msg
    try:
        await data["msg"].delete()
    except:
        pass

    # ---------------- RENAME ----------------
    if data["mode"] == "rename":
        new_name = message.text

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

        # AUTO THUMB if not set
        if not thumb and file_msg.video:
            thumb = None

        await client.send_document(
            message.chat.id,
            new_path,
            thumb=thumb
        )

        os.remove(new_path)

        await status.delete()

    # ---------------- EDIT CAPTION ----------------
    elif data["mode"] == "edit":
        await file_msg.copy(
            chat_id=message.chat.id,
            caption=message.text
        )

    user_data.pop(user_id)

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
