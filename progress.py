# ==========================================
# AniToon Bot - PROGRESS BAR (FIXED)
# ==========================================

import time
import asyncio

# ---------------- FORMAT HELPERS ----------------
def format_bytes(size):
    return size / (1024 * 1024)

def format_speed(speed):
    return speed / (1024 * 1024)

# ---------------- GLOBAL CACHE (ANTI-SPAM) ----------------
_last_update_time = {}

# ---------------- MAIN PROGRESS FUNCTION ----------------
async def progress(current, total, message, start_time):

    try:
        uid = getattr(message.chat, "id", None)

        now = time.time()

        # anti spam: update only every 1 second per chat
        if uid in _last_update_time:
            if now - _last_update_time[uid] < 1:
                return

        _last_update_time[uid] = now

        percent = (current / total) * 100 if total else 0

        elapsed = now - start_time
        speed = current / (elapsed + 1)

        eta = (total - current) / (speed + 1)

        # bars
        filled = int(percent // 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = f"""
📥 Processing File...

[{bar}] {percent:.1f}%

📦 {format_bytes(current):.2f} MB / {format_bytes(total):.2f} MB
⚡ Speed: {format_speed(speed):.2f} MB/s
⏳ ETA: {int(eta)} sec
"""

        try:
            await message.edit_text(text, reply_markup=message.reply_markup)
        except:
            pass

    except:
        pass
