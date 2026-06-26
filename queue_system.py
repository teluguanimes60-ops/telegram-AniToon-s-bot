# ==========================================
# AniToon Bot - QUEUE SYSTEM (FIXED)
# ==========================================

import asyncio
import time

# ---------------- QUEUE STORAGE ----------------
active_users = set()
queue = asyncio.Queue()

MAX_USERS = 20

# ---------------- USER CONTROL ----------------
def add_user(uid):
    active_users.add(uid)

def remove_user(uid):
    active_users.discard(uid)

def is_full():
    return len(active_users) >= MAX_USERS

# ---------------- QUEUE ADD JOB ----------------
async def add_job(job):
    await queue.put(job)

# ---------------- PROCESS QUEUE ----------------
async def process_queue():

    while True:
        job = await queue.get()

        try:
            job_id = job["job_id"]
            handler = job["handler"]

            await handler(job_id)

        except Exception as e:
            print(f"Queue Error: {e}")

        finally:
            queue.task_done()

# ---------------- START QUEUE (FIXED FOR RENDER) ----------------
def start_queue():

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(process_queue())
    loop.run_forever()
