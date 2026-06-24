from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
from flask import Flask
import os, time, threading

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

flask_app = Flask(__name__)
user_data = {}

CHANNEL = "https://t.me/Anitoon_edit/33"

cancel_flag = {}

# ---------------- PROGRESS ----------------
async def progress(current, total, message, start, text):
    uid = message.chat.id

    if cancel_flag.get(uid):
        raise Exception("Cancelled")

    diff = time.time() - start
    if diff < 0.5:
        return

    percent = current * 100 / total
    speed = current / diff if diff else 0
    eta = (total - current) / speed if speed else 0

    mins, secs = divmod(int(eta), 60)

    bar = "█" * int(percent // 10) + "▒" * (10 - int(percent // 10))

    try:
        await message.edit_text(
            f"{text}\n\n[{bar}] {percent:.1f}%\n⏳ {mins}m {secs}s\n\n🔗 {CHANNEL}"
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
        [InlineKeyboardButton("⚡ Instant Rename", callback_data="instant")],
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


def process_btn(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔗 Channel", url=CHANNEL),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{uid}")
        ]
    ])


def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
    ])


# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 **AniToon Bot**",
        reply_markup=main_menu()
    )


# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    await query.answer()
    data = query.data
    uid = query.from_user.id

    if data.startswith("cancel_"):
        cancel_flag[uid] = True
        await query.message.edit_text("❌ Cancelled", reply_markup=back_btn())
        return

    if data == "back":
        await query.message.edit_text("🔥 Main Menu", reply_markup=main_menu())

    elif data == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=back_btn())

    elif data == "rename":
        user_data[uid] = {"mode": "rename"}
        await query.message.edit_text("📁 Send file to rename", reply_markup=back_btn())

    elif data == "instant":
        user_data[uid] = {"mode": "instant"}
        await query.message.edit_text("⚡ Send file (fast rename mode)", reply_markup=back_btn())

    elif data == "convert":
        await query.message.edit_text("🔄 Choose convert type:", reply_markup=convert_menu())

    elif data == "file_to_video":
        user_data[uid] = {"mode": "file_to_video"}
        await query.message.edit_text("📄 Send file", reply_markup=back_btn())

    elif data == "video_to_file":
        user_data[uid] = {"mode": "video_to_file"}
        await query.message.edit_text("🎬 Send video", reply_markup=back_btn())


# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    uid = message.from_user.id

    cancel_flag[uid] = False

    mode = user_data.get(uid, {}).get("mode", "rename")

    user_data[uid] = {
        "file_msg": message,
        "mode": mode
    }

    if mode == "rename":
        await message.reply_text("✏️ Send file name (without extension)")
    elif mode == "instant":
        await message.reply_text("⚡ Send file name (fast rename)")
    else:
        await process_file(client, message)


# ---------------- PROCESS ----------------
async def process_file(client, message):
    uid = message.from_user.id

    if cancel_flag.get(uid):
        return

    data = user_data.get(uid)
    if not data:
        return

    file_msg = data["file_msg"]
    mode = data["mode"]

    msg = await message.reply_text(
        "⏳ Processing...",
        reply_markup=process_btn(uid)
    )

    start = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(msg, start, "📥 Downloading")
    )

    if cancel_flag.get(uid):
        await msg.edit_text("❌ Cancelled")
        return

    # ---------------- CLEAN RENAME ----------------
    if mode in ["rename", "instant"]:
        if not message.text:
            await message.reply_text("❌ Send valid name")
            return

        name = message.text.strip()
        ext = file_path.split(".")[-1]
        new_path = os.path.join(os.path.dirname(file_path), f"{name}.{ext}")

    elif mode == "file_to_video":
        new_path = file_path + ".mp4"

    elif mode == "video_to_file":
        new_path = file_path + ".bin"

    else:
        return

    os.rename(file_path, new_path)

    thumb = get_thumb()

    if mode == "file_to_video":
        await message.reply_video(new_path, thumb=thumb)

    elif mode == "video_to_file":
        await message.reply_document(new_path)

    else:
        if file_msg.video:
            await message.reply_video(new_path, thumb=thumb)
        else:
            await message.reply_document(new_path, thumb=thumb)

    try:
        await msg.delete()
    except:
        pass

    os.remove(new_path)
    del user_data[uid]


# ---------------- TEXT HANDLER ----------------
@app.on_message(filters.text & ~filters.command(["start"]))
async def text_handler(client, message):
    uid = message.from_user.id

    if uid not in user_data:
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
