# ==========================
# AniToon Bot - PRO PROGRESS SYSTEM
# CLEAN + STABLE + NO SPAM
# ==========================

import time
import asyncio

# store last update time to avoid spam edits
_last_update = {}

# ---------------- PROGRESS BAR ----------------

def build_bar(percent):
    filled = int(percent / 5)
    empty = 20 - filled
    return "█" * filled + "░" * empty


# ---------------- FORMAT SPEED ----------------

def format_speed(speed):
    if speed > 1024 * 1024:
        return f"{speed / (1024 * 1024):.2f} MB/s"
    elif speed > 1024:
        return f"{speed / 1024:.2f} KB/s"
    else:
        return f"{speed:.0f} B/s"


# ---------------- MAIN PROGRESS ----------------

async def progress(current, total, message, start_time):

    try:
        now = time.time()

        # anti spam (update every 2 sec)
        if message.id in _last_update:
            if now - _last_update[message.id] < 2:
                return

        _last_update[message.id] = now

        if total == 0:
            return

        percent = (current / total) * 100

        elapsed = now - start_time
        if elapsed <= 0:
            elapsed = 1

        speed = current / elapsed

        eta = (total - current) / (speed + 1)

        bar = build_bar(percent)

        text = (
            "📥 **Processing File**\n\n"
            f"`[{bar}]`\n\n"
            f"📊 **Progress:** {percent:.2f}%\n\n"
            f"⚡ **Speed:** {format_speed(speed)}\n"
            f"📦 **Downloaded:** {current / (1024*1024):.2f} MB\n"
            f"💾 **Total:** {total / (1024*1024):.2f} MB\n"
            f"⏳ **ETA:** {int(eta)} sec\n"
        )

        try:
            await message.edit_text(
                text,
                reply_markup=message.reply_markup
            )
        except:
            pass

    except:
        pass
