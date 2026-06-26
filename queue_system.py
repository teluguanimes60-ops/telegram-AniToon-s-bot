# ==========================================================
# 🤖 AniToon's Bot - Queue System v2
# Render + Pyrogram Compatible
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
# USER FUNCTIONS
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
# WAITING QUEUE
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
# MAIN PROCESSOR
# ==========================================================

async def process_queue():

    global QUEUE_RUNNING

    if QUEUE_RUNNING:
        return

    QUEUE_RUNNING = True

    while True:

        if is_full():

            await asyncio.sleep(1)
            continue

        job = await next_job()

        if job is None:

            await asyncio.sleep(0.5)
            continue

        try:

            uid = job["uid"]

            handler = job["handler"]

            add_user(uid)

            asyncio.create_task(run_job(uid, handler))

        except Exception as e:

            print("QUEUE ERROR:", e)


# ==========================================================
# RUN SINGLE JOB
# ==========================================================

async def run_job(uid, handler):

    try:

        await handler()

    except Exception as e:

        print("JOB ERROR:", e)

    finally:

        remove_user(uid)


# ==========================================================
# START QUEUE
# ==========================================================

def start_queue(app=None):
    """
    Call this ONCE after app.start()

    Example:

        app.start()
        start_queue(app)
        idle()
    """

    asyncio.get_running_loop().create_task(process_queue())
