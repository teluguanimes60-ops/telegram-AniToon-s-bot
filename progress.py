import time

# store last update time to avoid spam edits
last_update_time = {}


async def progress(current, total, message, start_time):
    """
    Clean progress bar for download/upload
    """

    try:
        now = time.time()

        # avoid editing too fast (Telegram flood control fix)
        if message.id in last_update_time:
            if now - last_update_time[message.id] < 1.5:
                return

        last_update_time[message.id] = now

        if total == 0:
            return

        # percentage
        percent = (current / total) * 100

        # time & speed
        elapsed = now - start_time
        if elapsed <= 0:
            elapsed = 1

        speed = current / elapsed

        # ETA
        eta = int((total - current) / (speed + 1))

        # MB conversion
        current_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        speed_mb = speed / (1024 * 1024)

        # progress bar
        filled = int(percent / 5)
        bar = "█" * filled + "░" * (20 - filled)

        text = (
            "📥 <b>Downloading...</b>\n\n"
            f"[{bar}]\n\n"
            f"📊 <b>{percent:.1f}%</b>\n\n"
            f"⚡ <b>Speed:</b> {speed_mb:.2f} MB/s\n"
            f"📦 <b>Done:</b> {current_mb:.2f} MB\n"
            f"💾 <b>Total:</b> {total_mb:.2f} MB\n"
            f"⏳ <b>ETA:</b> {eta} sec"
        )

        try:
            await message.edit_text(
                text,
                reply_markup=message.reply_markup,
                parse_mode="html"
            )
        except:
            pass

    except:
        pass
