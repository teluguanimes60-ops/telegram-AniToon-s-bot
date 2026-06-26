# ==========================================================
# 🤖 AniToon's Bot - Production Progress System
# ==========================================================

import time

from buttons import download_buttons, upload_buttons

# ----------------------------------------------------------
# Prevent FloodWait by limiting edit frequency
# ----------------------------------------------------------

_LAST_UPDATE = {}


# ----------------------------------------------------------
# Human Readable Size
# ----------------------------------------------------------

def human_bytes(size):

    if size is None:
        return "0 B"

    size = float(size)

    units = ["B", "KB", "MB", "GB", "TB"]

    power = 1024

    n = 0

    while size >= power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


# ----------------------------------------------------------
# ETA Format
# ----------------------------------------------------------

def human_time(seconds):

    seconds = int(seconds)

    m, s = divmod(seconds, 60)

    h, m = divmod(m, 60)

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


# ----------------------------------------------------------
# Progress Callback
# stage = download / upload
# ----------------------------------------------------------

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

        elapsed = now - start_time

        if elapsed <= 0:
            elapsed = 1

        percent = current * 100 / total

        speed = current / elapsed

        eta = (total - current) / speed if speed else 0

        filled = int(percent / 10)

        bar = "█" * filled + "░" * (10 - filled)

        if stage == "download":

            title = "📥 Downloading File"

            keyboard = download_buttons()

        else:

            title = "📤 Uploading File"

            keyboard = upload_buttons()

        text = (
            f"{title}\n\n"
            f"[{bar}] {percent:.1f}%\n\n"
            f"📦 {human_bytes(current)} / {human_bytes(total)}\n"
            f"⚡ Speed : {human_bytes(speed)}/s\n"
            f"⏳ ETA : {human_time(eta)}"
        )

        await message.edit_text(
            text,
            reply_markup=keyboard
        )

    except Exception:
        pass
