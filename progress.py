# progress.py

import time

last_update = {}


async def progress(current, total, message, start_time):
    """
    Progress bar for Download & Upload
    """

    now = time.time()

    if message.id in last_update:
        if now - last_update[message.id] < 2:
            return

    last_update[message.id] = now

    if total == 0:
        return

    percentage = current * 100 / total

    filled = int(percentage / 5)
    empty = 20 - filled

    bar = "█" * filled + "░" * empty

    elapsed = now - start_time

    if elapsed <= 0:
        elapsed = 1

    speed = current / elapsed

    if speed > 1024 * 1024:
        speed_text = f"{speed / 1024 / 1024:.2f} MB/s"
    elif speed > 1024:
        speed_text = f"{speed / 1024:.2f} KB/s"
    else:
        speed_text = f"{speed:.0f} B/s"

    eta = 0

    if speed > 0:
        eta = int((total - current) / speed)

    text = (
        "📥 **Processing File**\n\n"
        f"`[{bar}]`\n\n"
        f"**{percentage:.1f}%**\n\n"
        f"⚡ **Speed:** {speed_text}\n"
        f"📦 **Done:** {current/1024/1024:.2f} MB\n"
        f"💾 **Total:** {total/1024/1024:.2f} MB\n"
        f"⏳ **ETA:** {eta} sec"
    )

    try:
        await message.edit_text(
            text,
            reply_markup=message.reply_markup
        )
    except:
        pass
