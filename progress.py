# progress.py (PRO LEVEL UPGRADE)

import time
import asyncio

# store last update time per message (anti-spam)
last_update_time = {}


async def progress(current, total, message, start_time):

    try:
        if total == 0:
            return

        msg_id = message.id
        now = time.time()

        # ---------------- ANTI SPAM CONTROL ----------------
        if msg_id in last_update_time:
            if now - last_update_time[msg_id] < 1.5:
                return

        last_update_time[msg_id] = now

        # ---------------- PERCENT ----------------
        percent = (current / total) * 100

        # ---------------- SPEED ----------------
        elapsed = now - start_time
        if elapsed <= 0:
            elapsed = 1

        speed = current / elapsed  # bytes/sec

        speed_mb = speed / (1024 * 1024)
        done_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        # ---------------- ETA ----------------
        if speed > 0:
            eta = int((total - current) / speed)
        else:
            eta = 0

        # ---------------- PROGRESS BAR ----------------
        filled = int(percent / 5)
        empty = 20 - filled

        bar = "█" * filled + "░" * empty

        # ---------------- UI TEXT ----------------
        text = f"""
📥 **Processing File**

[{bar}]

📊 **{percent:.1f}%**

⚡ **Speed:** {speed_mb:.2f} MB/s
📦 **Done:** {done_mb:.2f} MB / {total_mb:.2f} MB
⏳ **ETA:** {eta} sec

━━━━━━━━━━━━━━
🚀 AniToon Bot
"""

        # ---------------- SAFE EDIT ----------------
        try:
            await message.edit_text(
                text,
                reply_markup=message.reply_markup
            )
        except:
            pass

    except:
        pass