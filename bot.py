import os
import time
import asyncio
import subprocess
import threading
import uuid

from flask import Flask

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from auto_thumb import (
    generate_thumbnail,
    setup_ffmpeg,
    FFMPEG_PATH
)

from thumbnail import (
    save_thumb,
    get_thumb
)

from help_text import HELP_TEXT

# ---------------- ENV ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise Exception("❌ Missing API_ID / API_HASH / BOT_TOKEN")

setup_ffmpeg()

# ---------------- FLASK ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "AniToon Bot Alive ✅"

threading.Thread(
    target=lambda: web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    ),
    daemon=True
).start()

# ---------------- BOT ----------------

app = Client(
    "AniToonBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# ---------------- DATABASE ----------------

user_states = {}
jobs = {}
user_last_msg = {}

# ---------------- CLEAN UI ----------------

async def clean_old(uid, msg):

    old = user_last_msg.get(uid)

    if old:
        try:
            await old.delete()
        except:
            pass

    user_last_msg[uid] = msg

# ---------------- BUTTONS ----------------

def main_menu():

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert File", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

def back_btn():

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])

def process_buttons(job_id):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⏸ Pause",
                callback_data=f"pause_{job_id}"
            ),
            InlineKeyboardButton(
                "▶ Resume",
                callback_data=f"resume_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data=f"cancel_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url="https://t.me/Anitoon_edit/33"
            )
        ]
    ])

def thumb_buttons(job_id):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📌 Saved Thumb",
                callback_data=f"thumb_saved_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ Auto Thumb",
                callback_data=f"thumb_auto_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No Thumb",
                callback_data=f"thumb_none_{job_id}"
            )
        ]
    ])

def convert_buttons(job_id):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📹 Convert To Video",
                callback_data=f"conv_video_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📁 Convert To File",
                callback_data=f"conv_file_{job_id}"
            )
        ]
    ])

# ---------------- JOB CREATE ----------------

def create_job(uid, file_msg, mode):

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "uid": uid,
        "file": file_msg,
        "mode": mode,
        "new_name": None,
        "thumb_mode": None,
        "convert_type": None,
        "control": "run"
    }

    return job_id

# ---------------- START ----------------

@app.on_message(filters.command("start"))
async def start(_, msg):

    name = msg.from_user.first_name or "User"

    text = f"""
👋 Hello {name}

📁 Rename Files
🔄 Convert Files
🖼 Thumbnail System
⚡ Instant Edit

━━━━━━━━━━━━━━

🔥 AniToon Rename Bot 

📢 Powered By: @AniToon_Edit
"""

    m = await msg.reply_text(
        text,
        reply_markup=main_menu()
    )

    await clean_old(
        msg.from_user.id,
        m
    )

# ---------------- CALLBACK HANDLER ----------------

@app.on_callback_query()
async def callback_handler(_, q):

    uid = q.from_user.id
    data = q.data

    # BACK
    if data == "back":

        user_states[uid] = {}

        m = await q.message.reply_text(
            "🔥 Main Menu",
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # RENAME
    elif data == "rename":

        user_states[uid] = {
            "mode": "rename",
            "step": "file"
        }

        m = await q.message.reply_text(
            "📁 Send File To Rename",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # CONVERT
    elif data == "convert":

        user_states[uid] = {
            "mode": "convert",
            "step": "file"
        }

        m = await q.message.reply_text(
            "🔄 Send Video/File To Convert",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # THUMBNAIL
    elif data == "thumb":

        user_states[uid] = {
            "mode": "thumb"
        }

        m = await q.message.reply_text(
            "🖼 Send Thumbnail Photo",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # INSTANT EDIT
    elif data == "instant":

        user_states[uid] = {
            "mode": "instant",
            "step": "file"
        }

        m = await q.message.reply_text(
            "⚡ Send File\n\nThen send new name instantly",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)

    # HELP
    elif data == "help":

        m = await q.message.reply_text(
            HELP_TEXT,
            reply_markup=main_menu()
        )

        await clean_old(uid, m)

    # PAUSE
    elif data.startswith("pause_"):

        job_id = data.replace("pause_", "")

        if job_id in jobs:
            jobs[job_id]["control"] = "pause"

        await q.answer("⏸ Paused")

    # RESUME
    elif data.startswith("resume_"):

        job_id = data.replace("resume_", "")

        if job_id in jobs:
            jobs[job_id]["control"] = "run"

        await q.answer("▶ Resumed")

    # CANCEL
    elif data.startswith("cancel_"):

        job_id = data.replace("cancel_", "")

        if job_id in jobs:
            jobs[job_id]["control"] = "cancel"

        await q.answer("❌ Cancelled")

    # SAVED THUMB
    elif data.startswith("thumb_saved_"):

        job_id = data.replace("thumb_saved_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "saved"

            await q.message.reply_text(
                "📹 Choose Output Type",
                reply_markup=convert_buttons(job_id)
            )

        await q.answer("Saved Thumb Selected")

    # AUTO THUMB
    elif data.startswith("thumb_auto_"):

        job_id = data.replace("thumb_auto_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "auto"

            await q.message.reply_text(
                "📹 Choose Output Type",
                reply_markup=convert_buttons(job_id)
            )

        await q.answer("Auto Thumb Selected")

    # NO THUMB
    elif data.startswith("thumb_none_"):

        job_id = data.replace("thumb_none_", "")

        if job_id in jobs:
            jobs[job_id]["thumb_mode"] = "none"

            await q.message.reply_text(
                "📹 Choose Output Type",
                reply_markup=convert_buttons(job_id)
            )

        await q.answer("No Thumb Selected")

    # CONVERT VIDEO
    elif data.startswith("conv_video_"):

        job_id = data.replace("conv_video_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "video"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📹 Video Selected")

    # CONVERT FILE
    elif data.startswith("conv_file_"):

        job_id = data.replace("conv_file_", "")

        if job_id in jobs:
            jobs[job_id]["convert_type"] = "file"

        asyncio.create_task(
            process_job(job_id)
        )

        await q.answer("📁 File Selected")

# ---------------- FILE HANDLER ----------------

@app.on_message(
    filters.document |
    filters.video |
    filters.audio
)
async def file_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    # RENAME
    if state.get("mode") == "rename":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "✏️ Send New File Name\n\n(Without Extension)",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # INSTANT EDIT
    if state.get("mode") == "instant":

        state["file"] = msg
        state["step"] = "name"

        m = await msg.reply_text(
            "⚡ Send New Name Instantly",
            reply_markup=back_btn()
        )

        await clean_old(uid, m)
        return

    # CONVERT
    if state.get("mode") == "convert":

        job_id = create_job(
            uid,
            msg,
            "convert"
        )

        m = await msg.reply_text(
            "🖼 Choose Thumbnail Type",
            reply_markup=thumb_buttons(job_id)
        )

        await clean_old(uid, m)

# ---------------- TEXT HANDLER ----------------

@app.on_message(filters.text & ~filters.command("start"))
async def text_handler(_, msg):

    uid = msg.from_user.id

    state = user_states.get(uid)

    if not state:
        return

    # NORMAL RENAME
    if (
        state.get("mode") == "rename"
        and
        state.get("step") == "name"
    ):

        job_id = create_job(
            uid,
            state["file"],
            "rename"
        )

        jobs[job_id]["new_name"] = msg.text

        m = await msg.reply_text(
            "⚙️ Starting Rename...",
            reply_markup=process_buttons(job_id)
        )

        jobs[job_id]["status"] = m

        asyncio.create_task(
            process_job(job_id)
        )

        user_states[uid] = {}
        return

    # INSTANT EDIT
    if (
        state.get("mode") == "instant"
        and
        state.get("step") == "name"
    ):

        job_id = create_job(
            uid,
            state["file"],
            "rename"
        )

        jobs[job_id]["new_name"] = msg.text

        m = await msg.reply_text(
            "⚡ Instant Edit Started...",
            reply_markup=process_buttons(job_id)
        )

        jobs[job_id]["status"] = m

        asyncio.create_task(
            process_job(job_id)
        )

        user_states[uid] = {}
        return

# ---------------- TEXT HANDLER ----------------

@app.on_message(filters.text & ~filters.command(["start"]))
async def text_handler(_, msg):

    uid = msg.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    # RENAME
    if (
        state.get("mode") == "rename"
        and
        state.get("step") == "name"
    ):

        file_msg = state["file"]

        job_id = create_job(
            uid,
            file_msg,
            "rename"
        )

        jobs[job_id]["new_name"] = msg.text

        m = await msg.reply_text(
            "🖼 Choose Thumbnail",
            reply_markup=thumb_buttons(job_id)
        )

        jobs[job_id]["status_msg"] = m

        user_states.pop(uid, None)

        return

    # INSTANT EDIT
    if (
        state.get("mode") == "instant"
        and
        state.get("step") == "name"
    ):

        file_msg = state["file"]

        job_id = create_job(
            uid,
            file_msg,
            "rename"
        )

        jobs[job_id]["new_name"] = msg.text

        m = await msg.reply_text(
            "🖼 Choose Thumbnail",
            reply_markup=thumb_buttons(job_id)
        )

        jobs[job_id]["status_msg"] = m

        user_states.pop(uid, None)

        return

# ---------------- THUMB CALLBACKS ----------------

@app.on_callback_query(filters.regex("^thumb_"))
async def thumb_select(_, q):

    data = q.data

    if data.startswith("thumb_saved_"):
        job_id = data.replace("thumb_saved_", "")
        jobs[job_id]["thumb_mode"] = "saved"

    elif data.startswith("thumb_auto_"):
        job_id = data.replace("thumb_auto_", "")
        jobs[job_id]["thumb_mode"] = "auto"

    elif data.startswith("thumb_none_"):
        job_id = data.replace("thumb_none_", "")
        jobs[job_id]["thumb_mode"] = "none"

    else:
        return

    job = jobs.get(job_id)

    if not job:
        return

    if job["mode"] == "convert":

        await q.message.edit_text(
            "🔄 Select Convert Type",
            reply_markup=convert_buttons(job_id)
        )

    else:

        await q.message.edit_text(
            "⚡ Starting Rename..."
        )

        asyncio.create_task(
            process_job(job_id)
        )

# ---------------- PROCESS JOB ----------------

async def process_job(job_id):

    job = jobs.get(job_id)

    if not job:
        return

    file_msg = job["file"]

    status = await file_msg.reply_text(
        "📥 Downloading...",
        reply_markup=process_buttons(job_id)
    )

    start_time = time.time()

    try:

        file_path = await file_msg.download(
            progress=progress,
            progress_args=(
                status,
                start_time
            )
        )

        # PAUSE SYSTEM
        while job["control"] == "pause":
            await asyncio.sleep(1)

        if job["control"] == "cancel":

            await status.edit_text(
                "❌ Cancelled"
            )

            return

        await status.edit_text(
            "⚙️ Processing...",
            reply_markup=process_buttons(job_id)
        )

        # THUMBNAIL
        thumb = None

        if job["thumb_mode"] == "saved":
            thumb = get_thumb()

        elif job["thumb_mode"] == "auto":
            thumb = generate_thumbnail(
                file_path
            )

        # RENAME
        if job["mode"] == "rename":

            ext = os.path.splitext(
                file_path
            )[1]

            new_path = (
                job["new_name"]
                + ext
            )

            os.rename(
                file_path,
                new_path
            )

            file_path = new_path

        # CONVERT
        elif job["mode"] == "convert":

            if job["convert_type"] == "video":

                output = (
                    file_path
                    + ".mp4"
                )

                subprocess.run(
                    [
                        FFMPEG_PATH,
                        "-i",
                        file_path,
                        output
                    ]
                )

                file_path = output

        await status.edit_text(
            "📤 Uploading...",
            reply_markup=process_buttons(job_id)
        )

        await file_msg.reply_document(
            document=file_path,
            thumb=thumb
        )

        await status.edit_text(
            "✅ Completed"
        )

    except Exception as e:

        await status.edit_text(
            f"❌ Error\n\n{e}"
        )

    finally:

        try:
            os.remove(file_path)
        except:
            pass

        jobs.pop(
            job_id,
            None
        )

# ---------------- START BOT ----------------

if __name__ == "__main__":

    print(
        "🚀 AniToon Bot Started"
    )

    app.run()
