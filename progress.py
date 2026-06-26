# ===========================
# AniToon Bot V3 - Progress FIX
# DOWNLOAD + UPLOAD PROGRESS
# ===========================

import time

last_update = {}


def format_speed(speed):
    if speed > 1024 * 1024:
        return f"{speed / 1024 / 1024:.2f} MB/s"
    elif speed > 1024:
        return f"{speed / 1024:.2f} KB/s"
    return f"{speed:.0f} B/s"


async def progress(current, total, message, start_time):

    try:
        now = time.time()

        if message.id in last_update:
            if now - last_update[message.id] < 1:
                return

        last_update[message.id] = now

        if total == 0:
            return

        percent = current * 100 / total

        elapsed = now - start_time
        speed = current / (elapsed + 1)

        eta = (total - current) / (speed + 1)

        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = (
            "📥 **Processing File**\n\n"
            f"`[{bar}]`\n\n"
            f"📊 **{percent:.1f}%**\n\n"
            f"⚡ **Speed:** {format_speed(speed)}\n"
            f"📦 **Done:** {current/1024/1024:.2f} MB\n"
            f"💾 **Total:** {total/1024/1024:.2f} MB\n"
            f"⏳ **ETA:** {int(eta)} sec"
        )

        try:
            await message.edit_text(text, reply_markup=message.reply_markup)
        except:
            pass

    except:
        pass
