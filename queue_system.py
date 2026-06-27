# ==========================================================
# 🤖 AniToon Bot - Queue System (Production v5)
# ==========================================================

import asyncio
from collections import deque

from jobs import get_user_job

# ==========================================================
# CONFIG
# ==========================================================

MAX_ACTIVE_USERS = 20

# ==========================================================
# STORAGE
# ==========================================================

ACTIVE_USERS = set()

WAITING_QUEUE = deque()

QUEUE_LOCK = asyncio.Lock()

QUEUE_RUNNING = False

# ==========================================================
# ACTIVE USERS
# ==========================================================

def active_count():
    return len(ACTIVE_USERS)


def queue_count():
    return len(WAITING_QUEUE)


def queue_size():
    return len(WAITING_QUEUE)


def is_full():
    return len(ACTIVE_USERS) >= MAX_ACTIVE_USERS


def user_processing(user_id):
    return user_id in ACTIVE_USERS


# ==========================================================
# QUEUE POSITION
# ==========================================================

def queue_position(user_id):

    pos = 1

    for job in WAITING_QUEUE:

        if job["uid"] == user_id:
            return pos

        pos += 1

    return 0


# ==========================================================
# ADD USER
# ==========================================================

def add_active(user_id):
    ACTIVE_USERS.add(user_id)


def remove_active(user_id):
    ACTIVE_USERS.discard(user_id)


# ==========================================================
# ADD TO QUEUE
# ==========================================================

async def add_to_queue(job):

    async with QUEUE_LOCK:

        uid = job["uid"]

        # Already processing
        if uid in ACTIVE_USERS:
            return False

        # Already waiting
        for j in WAITING_QUEUE:
            if j["uid"] == uid:
                return False

        # Already has unfinished job
        if get_user_job(uid):
            return False

        WAITING_QUEUE.append(job)

        return True


# ==========================================================
# NEXT JOB
# ==========================================================

async def next_job():

    async with QUEUE_LOCK:

        if not WAITING_QUEUE:
            return None

        return WAITING_QUEUE.popleft()


# ==========================================================
# REMOVE WAITING JOB
# ==========================================================

async def remove_waiting(user_id):

    async with QUEUE_LOCK:

        for job in list(WAITING_QUEUE):

            if job["uid"] == user_id:

                WAITING_QUEUE.remove(job)

                return True

    return False


# ==========================================================
# CLEAR QUEUE
# ==========================================================

async def clear_queue():

    async with QUEUE_LOCK:
        WAITING_QUEUE.clear()


# ==========================================================
# RUN JOB
# ==========================================================

async def run_job(job):

    uid = job["uid"]

    handler = job["handler"]

    add_active(uid)

    try:

        await handler()

    except Exception as e:

        print(f"[QUEUE] Job Error ({uid}) :", e)

    finally:

        remove_active(uid)


# ==========================================================
# MAIN LOOP
# ==========================================================

async def process_queue():

    global QUEUE_RUNNING

    if QUEUE_RUNNING:
        return

    QUEUE_RUNNING = True

    print("✅ Queue Processor Started")

    while True:

        try:

            if is_full():
                await asyncio.sleep(1)
                continue

            job = await next_job()

            if job is None:
                await asyncio.sleep(0.5)
                continue

            asyncio.create_task(run_job(job))

        except Exception as e:

            print("[QUEUE ERROR]", e)

            await asyncio.sleep(1)


# ==========================================================
# START
# ==========================================================

async def start_queue():

    await process_queue()
