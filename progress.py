import time

last_update = {}

async def progress(current, total, message, start):

    uid = message.chat.id
    now = time.time()

    # anti-spam update (important fix)
    if uid in last_update and now - last_update[uid] < 2:
        return

    last_update[uid] = now

    try:
        percent = (current / total) * 100 if total else 0
        speed = current / (now - start + 0.1)

        bar = "█" * int(percent / 10) + "░" * (10 - int(percent / 
