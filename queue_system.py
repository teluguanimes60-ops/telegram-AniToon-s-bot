# ==========================================================
# 🤖 AniToon Bot - Queue System v3 (Stable)
# Compatible with bot.py + engine.py
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

QUEUE_RUNNING = False

QUEUE_LOCK = asyncio.Lock()

# ==========================================================
# ACTIVE USER FUNCTIONS
# ==========================================================

def active_count():
    return len(ACTIVE_USERS)


def is_full():
    return len(ACTIVE_USERS) >= MAX_ACTIVE_USERS


def user_processing(user_id):
    return user_id in ACTIVE_USERS


def add_user(user_id):
    ACTIVE_USERS.add(user_id)


def remove_user(user_id):
    ACTIVE_USERS.discard(user_id)

# ==========================================================
# QUEUE FUNCTIONS
# ==========================================================

async def add_to_queue(job):
    async with QUEUE_LOCK:
        WAITING_QUEUE.append(job)


async def next_job():
    async with QUEUE_LOCK:

        if not WAITING_QUEUE:
            return None

        return WAITING_QUEUE.popleft()

# ==========================================================
# RUN SINGLE JOB
# ==========================================================

async def run_job(job):

    uid = job["uid"]

    try:

        add_user(uid)

        await job["handler"]()

    except Exception as e:

        print("JOB ERROR:", e)

    finally:

        remove_user(uid)

# ==========================================================
# MAIN QUEUE LOOP
# ==========================================================

async def process_queue():

    global QUEUE_RUNNING

    if QUEUE_RUNNING:
        return

    QUEUE_RUNNING = True

    print("✅ Queue Started")

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

            print("QUEUE ERROR:", e)

            await asyncio.sleep(1)

# ==========================================================
# START QUEUE
# ==========================================================

def start_queue():

    loop = asyncio.get_event_loop()

    loop.create_task(process_queue())
