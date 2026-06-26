# ==========================================
# AniToon Bot - STABLE PROGRESS ENGINE
# ==========================================

import time

last_update = {}

# ==========================================
async def progress(current, total, message, start):

    try:

        key = message.chat.id

        now = time.time()

        # throttle updates (VERY IMPORTANT)
        if key in last_update and now - last_update[key] < 1.5:
            return

        last_update[key] = now

        percent = (current * 100) / total if total else 0

        elapsed = now - start
        speed = current / elapsed if elapsed > 0 else 0

        eta = (total - current) / speed if speed > 0 else 0

        bar = "█" * int(percent // 10) + "░" * (10 - int(percent // 10))

        text = (
            f"📦 Uploading...\n\n"
            f"[{bar}] {percent:.1f}%\n"
            f"⚡ Speed: {speed/1024/1024:.2f} MB/s\n"
            f"⏳ ETA: {int(eta)} sec"
        )

        await message.edit_text(text)

    except:
        pass
