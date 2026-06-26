# ==========================================
# AniToon Bot - PRODUCTION QUEUE ENGINE v4
# ==========================================

import asyncio
import time

MAX_ACTIVE_USERS = 20

active_users = set()
waiting_queue = []

user_last_seen = {}

# ==========================================
# 👤 ADD USER TO SYSTEM
# ==========================================
def add_user(uid: int) -> bool:
    """
    Returns True if user can process immediately
    Returns False if user is queued
    """

    user_last_seen[uid] = time.time()

    # already active
    if uid in active_users:
        return True

    # space available
    if len(active_users) < MAX_ACTIVE_USERS:
        active_users.add(uid)
        return True

    # already in queue
    if uid not in waiting_queue:
        waiting_queue.append(uid)

    return False

# ==========================================
# ❌ REMOVE USER FROM ACTIVE
# ==========================================
def remove_user(uid: int):

    if uid in active_users:
        active_users.remove(uid)

# ==========================================
# 📊 GET QUEUE POSITION
# ==========================================
def get_position(uid: int) -> int:

    if uid in active_users:
        return 0

    if uid in waiting_queue:
        return waiting_queue.index(uid) + 1

    return -1

# ==========================================
# 🧠 CLEAN DEAD USERS
# ==========================================
def cleanup(timeout: int = 600):

    now = time.time()

    # remove inactive users from queue
    for uid in waiting_queue[:]:
        if now - user_last_seen.get(uid, 0) > timeout:
            waiting_queue.remove(uid)

# ==========================================
# 🚀 PROMOTE QUEUE USERS
# ==========================================
async def process_queue():

    while True:

        try:
            cleanup()

            while waiting_queue and len(active_users) < MAX_ACTIVE_USERS:

                uid = waiting_queue.pop(0)

                if uid not in active_users:
                    active_users.add(uid)

        except:
            pass

        await asyncio.sleep(2)

# ==========================================
# ▶ START QUEUE WORKER
# ==========================================
def start_queue():

    asyncio.create_task(process_queue())
