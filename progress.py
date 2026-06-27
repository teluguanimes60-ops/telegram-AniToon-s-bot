# ==========================================================
# 🤖 AniToon Bot - Progress System (Production V8)
# ==========================================================

import time
import asyncio

from buttons import download_buttons, upload_buttons
from states import get_state

# ==========================================================
# FLOOD CONTROL
# ==========================================================

LAST_UPDATE = {}
UPDATE_INTERVAL = 2

# ==========================================================
# HUMAN SIZE
# ==========================================================

def human_size(size):

    size = float(size)

    for unit in ("B", "KB", "MB", "GB", "TB"):

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"

# ==========================================================
# HUMAN TIME
# ==========================================================

def human_time(seconds):

    seconds = max(int(seconds), 0)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"

# ==========================================================
# BAR
# ==========================================================

def progress_bar(percent):

    total = 20

    filled = int(total * percent / 100)

    return "█" * filled + "░" * (total - filled)

# ==========================================================
# CALLBACK
# ==========================================================

async def progress(
    current,
    total,
    message,
    start,
    stage="download"
):

    user_id = message.chat.id

    state = get_state(user_id)

    while state.get("paused", False):
        await asyncio.sleep(0.5)

    if state.get("cancelled", False):
        raise Exception("Cancelled")

    now = time.time()

    if (
        message.id in LAST_UPDATE
        and now - LAST_UPDATE[message.id] < UPDATE_INTERVAL
    ):
        return

    LAST_UPDATE[message.id] = now

    try:

        elapsed = max(now - start, 1)

        speed = current / elapsed

        percent = (current / total) * 100 if total else 0

        eta = (
            (total - current) / speed
            if speed > 0 else 0
        )

        title = (
            "📥 Downloading..."
            if stage == "download"
            else "📤 Uploading..."
        )

        text = (
            f"{title}\n\n"
            f"{progress_bar(percent)}\n\n"
            f"**{percent:.2f}%**\n\n"
            f"📦 {human_size(current)} / {human_size(total)}\n"
            f"⚡ {human_size(speed)}/s\n"
            f"⏳ ETA : {human_time(eta)}"
        )

        if stage == "download":

            await message.edit_text(
                text,
                reply_markup=download_buttons()
            )

        else:

            await message.edit_text(
                text,
                reply_markup=upload_buttons()
            )

    except Exception:
        pass
