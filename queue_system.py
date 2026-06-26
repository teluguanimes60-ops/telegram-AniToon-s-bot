# ==========================================
# AniToon Bot - QUEUE SYSTEM (PRO FIXED)
# ==========================================

import asyncio
import time

MAX_USERS = 20

active_users = set()        # users currently processing
waiting_queue = []          # queued user IDs (FIFO)

# ---------------- CHECK LIMIT ----------------
def can_process(uid: int) -> bool:
    return uid in active_users or len(active_users) < MAX_USERS

# ---------------- ADD USER ----------------
def add_user(uid: int):
    if uid in active_users:
        return True

    if len(active_users) < MAX_USERS:
        active_users.add(uid)
        return True

    if uid not in waiting_queue:
        waiting_queue.append(uid)

    return False

# ---------------- REMOVE USER ----------------
def remove_user(uid: int):
    if uid in active_users:
        active_users.discard(uid)

# ---------------- GET STATUS ----------------
def is_waiting(uid: int) -> bool:
    return uid in waiting_queue

# ---------------- PROMOTE QUEUE ----------------
async def process_queue():
    while True:

        try:
            if waiting_queue and len(active_users) < MAX_USERS:

                uid = waiting_queue.pop(0)
                active_users.add(uid)

        except:
            pass

        await asyncio.sleep(2)

# ---------------- START QUEUE WORKER ----------------
def start_queue():
    asyncio.create_task(process_queue())
