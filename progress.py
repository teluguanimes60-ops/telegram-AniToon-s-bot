# ==========================================================
# 🤖 AniToon Bot - Progress System (Production v5)
# ==========================================================

import time

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================================
# CHANNEL
# ==========================================================

CHANNEL_URL = "https://t.me/Anitoon_edit/33"

# ==========================================================
# FLOOD PROTECTION
# ==========================================================

_LAST_UPDATE = {}

# ==========================================================
# HUMAN SIZE
# ==========================================================

def human_size(size):

    if not size:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size)

    i = 0

    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1

    return f"{size:.2f} {units[i]}"

# ==========================================================
# ETA
# ==========================================================

def human_time(seconds):

    seconds = int(seconds)

    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"

# ==========================================================
# PROGRESS BAR
# ==========================================================

def progress_bar(percent):

    filled = int(percent / 10)

    return "█" * filled + "░" * (10 - filled)

# ==========================================================
# DOWNLOAD BUTTONS
# ==========================================================

def download_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⏸ Pause",
                callback_data="pause"
            ),
            InlineKeyboardButton(
                "▶ Resume",
                callback_data="resume"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_job"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ]
    ])

# ==========================================================
# UPLOAD BUTTONS
# ==========================================================

def upload_keyboard():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_job"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ]
    ])

# ==========================================================
# MAIN CALLBACK
# ==========================================================

async def progress(
    current,
    total,
    message,
    start_time,
    stage="download"
):

    now = time.time()

    key = message.id

    if key in _LAST_UPDATE:

        if now - _LAST_UPDATE[key] < 2:
            return

    _LAST_UPDATE[key] = now

    try:

        elapsed = max(now - start_time, 1)

        percent = current * 100 / total if total else 0

        speed = current / elapsed

        eta = (total - current) / speed if speed else 0

        bar = progress_bar(percent)

        if stage == "download":

            title = "📥 Downloading..."

            keyboard = download_keyboard()

        else:

            title = "📤 Uploading..."

            keyboard = upload_keyboard()

        text = (
            f"{title}\n\n"
            f"[{bar}] {percent:.1f}%\n\n"
            f"📦 {human_size(current)} / {human_size(total)}\n"
            f"⚡ Speed : {human_size(speed)}/s\n"
            f"⏳ ETA : {human_time(eta)}"
        )

        await message.edit_text(
            text,
            reply_markup=keyboard
        )

    except Exception:
        pass
