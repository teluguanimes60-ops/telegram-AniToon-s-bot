# ==========================================================
# 🤖 AniToon Bot - Progress System (Production v6)
# ==========================================================

import time
from buttons import download_buttons, upload_buttons

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

    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size)

    while size >= power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


# ==========================================================
# HUMAN TIME
# ==========================================================

def human_time(seconds):

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

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

        percent = (current * 100) / total if total else 0

        speed = current / elapsed

        eta = (total - current) / speed if speed else 0

        text = (
            f"{'📥 Downloading File' if stage == 'download' else '📤 Uploading File'}\n\n"
            f"[{progress_bar(percent)}] {percent:.1f}%\n\n"
            f"📦 {human_size(current)} / {human_size(total)}\n"
            f"⚡ Speed : {human_size(speed)}/s\n"
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
