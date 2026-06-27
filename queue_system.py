# ==========================================================
# 🤖 AniToon Bot - Queue System (Production V7)
# ==========================================================

import asyncio
from collections import deque

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

QUEUE_STARTED = False

# ==========================================================
# STATUS
# ==========================================================

def active_count():
    return len(ACTIVE_USERS)


def queue_count():
    return len(WAITING_QUEUE)


def queue_size():
    return len(WAITING_QUEUE)


def user_processing(user_id):
    return user_id in ACTIVE_USERS


def is_full():
    return len(ACTIVE_USERS) >= MAX_ACTIVE_USERS

# ==========================================================
# SETTINGS
# ==========================================================

def set_max_active(limit):

    global MAX_ACTIVE_USERS

    MAX_ACTIVE_USERS = max(1, int(limit))

# ==========================================================
# POSITION
# ==========================================================

def queue_position(user_id):

    for i, job in enumerate(WAITING_QUEUE, start=1):

        if job["uid"] == user_id:
            return i

    return 0

# ==========================================================
# ACTIVE
# ==========================================================

def add_active(user_id):

    ACTIVE_USERS.add(user_id)


def remove_active(user_id):

    ACTIVE_USERS.discard(user_id)

# ==========================================================
# ADD JOB
# ==========================================================

async def add_to_queue(job):

    async with QUEUE_LOCK:

        uid = job["uid"]

        if uid in ACTIVE_USERS:
            return False

        for j in WAITING_QUEUE:

            if j["uid"] == uid:
                return False

        WAITING_QUEUE.append(job)

        return True

# ==========================================================
# REMOVE JOB
# ==========================================================

async def remove_waiting(user_id):

    async with QUEUE_LOCK:

        for job in list(WAITING_QUEUE):

            if job["uid"] == user_id:

                WAITING_QUEUE.remove(job)

                return True

    return False

# ==========================================================
# NEXT JOB
# ==========================================================

async def next_job():

    async with QUEUE_LOCK:

        if not WAITING_QUEUE:
            return None

        return WAITING_QUEUE.popleft()

# ==========================================================
# CLEAR
# ==========================================================

async def clear_queue():

    async with QUEUE_LOCK:

        WAITING_QUEUE.clear()

# ==========================================================
# RUN
# ==========================================================

async def run_job(job):

    uid = job["uid"]

    handler = job["handler"]

    add_active(uid)

    try:

        await handler()

    except Exception as e:

        print(f"[QUEUE] {uid}: {e}")

    finally:

        remove_active(uid)

# ==========================================================
# LOOP
# ==========================================================

async def process_queue():

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

    global QUEUE_STARTED

    if QUEUE_STARTED:
        return

    QUEUE_STARTED = True

    print("✅ Queue Started")

    asyncio.create_task(process_queue())
