# =========================
# AniToon Queue System
# =========================

import asyncio

MAX_WORKERS = 2
active_tasks = set()
waiting_queue = asyncio.Queue()

async def worker():
    while True:
        job = await waiting_queue.get()
        await job()
        waiting_queue.task_done()

def start_workers():
    for _ in range(MAX_WORKERS):
        asyncio.create_task(worker())

def add_job(job_func):
    if len(active_tasks) < MAX_WORKERS:
        active_tasks.add(job_func)
        asyncio.create_task(run(job_func))
    else:
        waiting_queue.put_nowait(job_func)

async def run(job_func):
    try:
        await job_func()
    finally:
        active_tasks.discard(job_func)
