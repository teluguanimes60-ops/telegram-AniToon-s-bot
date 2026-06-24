from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH
import os, time, re

from thumbnail import save_thumb, get_thumb
from help_text import HELP_TEXT

CHANNEL = "https://t.me/Anitoon_edit/33"

app = Client("AniToonBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- DATA ----------------
user_data = {}
cancel_flag = {}

# ---------------- CLEAN NAME ----------------
def clean_name(name: str):
    name = re.sub(r"\[.*?\]|\(.*?\)", "", name)
    name = re.sub(
        r"\b(720p|1080p|480p|BluRay|HDRip|WEB-DL|x264|x265|AAC|H264|H265)\b",
        "",
        name,
        flags=re.IGNORECASE
    )
    name = re.sub(r"\s+", " ", name)
    return name.strip(" -_.")


# ---------------- PROGRESS ----------------
async def progress(current, total, message, start, text):
    uid = message.chat.id

    if cancel_flag.get(uid):
        raise Exception("Cancelled")

    diff = time.time() - start
    if diff < 0.5:
        return

    percent = current * 100 / total if total else 0
    bar = "█" * int(percent // 10) + "▒" * (10 - int(percent // 10))

    try:
        await message.edit_text(
            f"{text}\n\n[{bar}] {percent:.1f}%\n\n🔗 {CHANNEL}"
        )
    except:
        pass


# ---------------- START ----------------
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "🔥 AniToon Bot",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📁 Rename", callback_data="rename")],
            [InlineKeyboardButton("⚡ Instant", callback_data="instant")],
            [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
            [InlineKeyboardButton("🖼 Thumb", callback_data="thumb")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
            [InlineKeyboardButton("🔗 Channel", url=CHANNEL)]
        ])
    )


# ---------------- CALLBACK ----------------
@app.on_callback_query()
async def cb(client, query):
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data == "rename":
        user_data[uid] = {"mode": "rename"}
        await query.message.edit_text("Send file for rename")

    elif data == "instant":
        user_data[uid] = {"mode": "instant"}
        await query.message.edit_text("⚡ Instant rename mode")

    elif data == "help":
        await query.message.edit_text(HELP_TEXT)

    elif data == "back":
        await query.message.edit_text("Main Menu")


# ---------------- FILE HANDLER ----------------
@app.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message):
    uid = message.from_user.id
    mode = user_data.get(uid, {}).get("mode", "rename")

    user_data[uid] = {"file_msg": message, "mode": mode}

    if mode == "rename":
        await message.reply_text("Send new file name")
    else:
        await process_file(message)


# ---------------- PROCESS ----------------
async def process_file(message):
    uid = message.from_user.id
    data = user_data.get(uid)

    file_msg = data["file_msg"]
    mode = data["mode"]

    msg = await message.reply_text("⏳ Processing...")

    start = time.time()

    file_path = await file_msg.download(
        progress=progress,
        progress_args=(msg, start, "Downloading")
    )

    if not message.text:
        return

    clean = clean_name(message.text)
    ext = file_path.split(".")[-1]
    new_path = os.path.join(os.path.dirname(file_path), f"{clean}.{ext}")

    os.rename(file_path, new_path)

    await message.reply_document(new_path)

    os.remove(new_path)
    del user_data[uid]
    await msg.delete()


# ---------------- RUN ----------------
if __name__ == "__main__":
    print("🚀 Bot Running...")
    app.run()
