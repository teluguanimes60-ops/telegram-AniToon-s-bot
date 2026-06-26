# ==========================================
# AniToon Bot - PRODUCTION QUEUE ENGINE v4 FIXED
# ==========================================

import asyncio
import time

MAX_ACTIVE_USERS = 20

active_users = set()
waiting_queue = []
user_last_seen = {}

# ==========================================
def add_user(uid: int) -> bool:

    user_last_seen[uid] = time.time()

    if uid in active_users:
        return True

    if len(active_users) < MAX_ACTIVE_USERS:
        active_users.add(uid)
        return True

    if uid not in waiting_queue:
        waiting_queue.append(uid)

    return False

# ==========================================
def remove_user(uid: int):
    active_users.discard(uid)

# ==========================================
def get_position(uid: int) -> int:

    if uid in active_users:
        return 0

    if uid in waiting_queue:
        return waiting_queue.index(uid) + 1

    return -1

# ==========================================
def cleanup(timeout: int = 600):

    now = time.time()

    for uid in waiting_queue[:]:
        if now - user_last_seen.get(uid, 0) > timeout:
            waiting_queue.remove(uid)

# ==========================================
async def process_queue():

    while True:

        try:

            cleanup()

            while waiting_queue and len(active_users) < MAX_ACTIVE_USERS:

                uid = waiting_queue.pop(0)

                if uid not in active_users:
                    active_users.add(uid)

        except Exception as e:
            print("Queue error:", e)

        await asyncio.sleep(2)

# ==========================================
# ✅ SAFE START FUNCTION (FIX)
# ==========================================
def start_queue(app):

    async def runner():
        await process_queue()

    # attach to running loop safely
    import threading

    def run():
        asyncio.run(runner())

    threading.Thread(target=run, daemon=True).start()
