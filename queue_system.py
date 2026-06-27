# ==========================================================
# 🤖 AniToon Bot - Queue System v4
# Stable | FIFO Queue | Max 20 Active Users
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

QUEUE_RUNNING = False

# ==========================================================
# ACTIVE USERS
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
# QUEUE
# ==========================================================

async def add_to_queue(job):
    async with QUEUE_LOCK:
        WAITING_QUEUE.append(job)


async def next_job():
    async with QUEUE_LOCK:

        if not WAITING_QUEUE:
            return None

        return WAITING_QUEUE.popleft()


def queue_size():
    return len(WAITING_QUEUE)

# ==========================================================
# RUN SINGLE JOB
# ==========================================================

async def run_job(job):

    uid = job["uid"]
    handler = job["handler"]

    add_user(uid)

    try:

        await handler()

    except Exception as e:

        print(f"JOB ERROR [{uid}] :", e)

    finally:

        remove_user(uid)

# ==========================================================
# MAIN QUEUE
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

            print("QUEUE ERROR:", e)

            await asyncio.sleep(1)

# ==========================================================
# START
# ==========================================================

async def start_queue():

    await process_queue()
