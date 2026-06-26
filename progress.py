# ==========================================
# AniToon Bot - PRO PROGRESS SYSTEM
# ==========================================

import time

# prevents spam editing (VERY IMPORTANT for Telegram)
last_update_time = {}

# ---------------- FORMAT SIZE ----------------
def human_readable(size):
    if size >= 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"
    elif size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size} B"


# ---------------- PROGRESS BAR ----------------
def make_bar(percent):
    filled = int(percent / 5)
    empty = 20 - filled
    return "█" * filled + "░" * empty


# ---------------- MAIN PROGRESS ----------------
async def progress(current, total, message, start_time):

    try:
        now = time.time()

        # 🔥 anti-spam (update only every 1.5 sec)
        if message.id in last_update_time:
            if now - last_update_time[message.id] < 1.5:
                return

        last_update_time[message.id] = now

        if total == 0:
            return

        percent = (current * 100) / total

        elapsed = now - start_time
        if elapsed <= 0:
            elapsed = 1

        speed = current / elapsed

        eta = (total - current) / (speed + 1)

        # format values
        bar = make_bar(percent)

        speed_text = human_readable(speed) + "/s"
        current_text = human_readable(current)
        total_text = human_readable(total)

        # 📥 DOWNLOAD / UPLOAD TEXT
        text = f"""
📥 **Processing File**

[{bar}]

📊 **Progress:** {percent:.2f}%

⚡ **Speed:** {speed_text}

📦 **Done:** {current_text} / {total_text}

⏳ **ETA:** {int(eta)} sec
"""

        # edit message safely
        await message.edit_text(
            text,
            reply_markup=message.reply_markup
        )

    except Exception:
        pass