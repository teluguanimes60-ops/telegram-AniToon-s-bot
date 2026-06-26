# ==========================================
# AniToon Bot - PROGRESS BAR (FIXED)
# ==========================================

import time

# ---------------- FORMAT SIZE ----------------
def human_bytes(size):
    if not size:
        return "0B"

    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]

    while size >= power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{round(size, 2)} {units[n]}"


# ---------------- PROGRESS CALLBACK ----------------
async def progress(current, total, message, start):

    try:
        now = time.time()
        diff = now - start

        if diff == 0:
            diff = 0.1

        speed = current / diff
        percent = (current * 100) / total

        # ETA
        eta = (total - current) / speed if speed > 0 else 0

        # BAR
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)

        text = f"""
📥 **Processing File**

[{bar}] {round(percent, 2)}%

📦 {human_bytes(current)} / {human_bytes(total)}
⚡ Speed: {human_bytes(speed)}/s
⏳ ETA: {int(eta)} sec
"""

        # EDIT MESSAGE SAFELY
        await message.edit_text(text)

    except Exception:
        pass
