from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

flask_app = Flask(__name__)
user_data = {}

# ---------------- CANCEL SYSTEM ----------------
cancel_tasks = {}

CHANNEL = "https://t.me/Anitoon_edit"


# ---------------- PROGRESS ----------------
async def progress(current, total, message, start, text):
    if cancel_tasks.get(message.chat.id):
        raise Exception("Cancelled")

    diff = time.time() - start
    if diff < 1:
        return

    percent = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed if speed > 0 else 0

    speed_text = f"{speed/1024/1024:.2f} MB/s" if speed > 1024*1024 else f"{speed/1024:.2f} KB/s"
    mins, secs = divmod(int(eta), 60)

    bar = "█" * int(percent // 10) + "░" * (10 - int(percent // 10))

    try:
        await message.edit_text(
            f"{text}\n\n[{bar}] {percent:.1f}%\n⚡ {speed_text}\n⏳ {mins}m {secs}s",
            reply_markup=cancel_btn(message.chat.id)
        )
    except:
        pass


# ---------------- BOT ----------------
app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ---------------- KEEP ALIVE ----------------
@flask_app.route("/")
def home():
    return "Bot Running"

def run():
    flask_app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run, daemon=True).start()


# ---------------- BUTTONS ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
    ])


def convert_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 File → Video", callback_data="file_to_video")],
        [InlineKeyboardButton("🎬 Video → File", callback_data="video_to_file")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
    ])


def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
    ])


def cancel_btn(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{uid}")],
        [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
    ])


# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 **AniToon Bot**\n\nSelect option:",
        reply_markup=main_menu()
    )


# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "back":
        await query.message.edit_text("🔥 Main Menu", reply_markup=main_menu())

    elif data == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=back_btn())

    elif data == "rename":
        user_data[uid] = {"mode": "rename"}
        await query.message.edit_text("📁 Send file to rename", reply_markup=back_btn())

    elif data == "thumb":
        await query.message.edit_text("🖼 Send photo to set thumbnail", reply_markup=back_btn())

    elif data == "convert":
        await query.message.edit_text("🔄 Choose convert type:", reply_markup=convert_menu())

    elif data == "file_to_video":
        user_data[uid] = {"mode": "file_to_video"}
        await query.message.edit_text("📄 Send file to convert into video", reply_markup=back_btn())

    elif data == "video_to_file":
        user_data[uid] = {"mode": "video_to_file"}
        await query.message.edit_text("🎬 Send video to convert into file", reply_markup=back_btn())

    elif data.startswith("cancel_"):
        cancel_tasks[uid] = True
        await query.message.edit_text("❌ Cancelled", reply_markup=back_btn())


# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    user_id = message.from_user.id

    mode = user_data.get(user_id, {}).get("mode", "rename")

    user_data[user_id] = {
        "file_msg": message,
        "mode": mode
    }

    if mode == "rename":
        await message.reply_text("✏️ Send new file name")
    else:
        await process_file(client, message, auto=True)


# ---------------- PROCESS ----------------
async def process_file(client, message, auto=False):
    user_id = message.from_user.id
    data = user_data.get(user_id)

    if not data:
        return

    cancel_tasks[user_id] = False

    file_msg = data["file_msg"]
    mode = data.get("mode", "rename")

    msg = await message.reply_text(
        "⏳ Processing...\nPress ❌ cancel if needed",
        reply_markup=cancel_btn(user_id)
    )

    start_time = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(msg, start_time, "📥 Downloading")
    )

    if cancel_tasks.get(user_id):
        await msg.edit_text("❌ Cancelled")
        return

    # ---------- RENAME ----------
    if mode == "rename" and not auto:
        if not message.text:
            await message.reply_text("❌ Send valid file name")
            return

        new_name = message.text.strip()
        ext = file_path.split(".")[-1]
        new_path = os.path.join(os.path.dirname(file_path), f"{new_name}.{ext}")

    elif mode == "file_to_video":
        new_path = file_path + ".mp4"

    elif mode == "video_to_file":
        new_path = file_path + ".bin"

    else:
        return

    os.rename(file_path, new_path)

    thumb = get_thumb()
    start_time = time.time()

    if cancel_tasks.get(user_id):
        await msg.edit_text("❌ Cancelled")
        return

    # ---------- SEND ----------
    if mode == "file_to_video":
        await message.reply_video(
            new_path,
            thumb=thumb,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    elif mode == "video_to_file":
        await message.reply_document(
            new_path,
            progress=progress,
            progress_args=(msg, start_time, "📤 Uploading")
        )

    else:
        if file_msg.video:
            await message.reply_video(new_path, thumb=thumb)
        elif file_msg.audio:
            await message.reply_audio(new_path)
        else:
            await message.reply_document(new_path, thumb=thumb)

    os.remove(new_path)
    del user_data[user_id]
    cancel_tasks.pop(user_id, None)


# ---------------- TEXT ----------------
@app.on_message(filters.text & ~filters.command(["start"]))
async def rename_input(client, message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    await process_file(client, message)


# ---------------- THUMB ----------------
@app.on_message(filters.photo)
async def thumb_handler(client, message):
    path = await message.download()
    save_thumb(path)
    await message.reply_text("✅ Thumbnail Saved")


print("🚀 Bot Running...")
app.run()
