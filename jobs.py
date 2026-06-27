# ==========================================================
# 🤖 AniToon Bot - Job Manager v4 (Stable)
# Thread-safe | Production Ready
# ==========================================================

import threading
import time

# ==========================================================
# STORAGE
# ==========================================================

JOBS = {}

LOCK = threading.Lock()

# ==========================================================
# DEFAULT JOB
# ==========================================================

DEFAULT_JOB = {
    "status": "pending",
    "file_path": None,
    "new_name": None,
    "mode": "rename",
    "thumb_mode": "auto"
}

# ==========================================================
# CREATE JOB
# ==========================================================

def create_job(job_id, uid, data=None):

    if data is None:
        data = {}

    job = {
        "job_id": job_id,
        "uid": uid,
        "created_at": time.time(),
        **DEFAULT_JOB,
        **data
    }

    with LOCK:
        JOBS[job_id] = job

    return job

# ==========================================================
# GET JOB
# ==========================================================

def get_job(job_id):

    with LOCK:
        job = JOBS.get(job_id)

    if job is None:
        return None

    return job

# ==========================================================
# UPDATE SINGLE FIELD
# ==========================================================

def update_job(job_id, key, value):

    with LOCK:

        if job_id not in JOBS:
            return False

        JOBS[job_id][key] = value

    return True

# ==========================================================
# UPDATE MULTIPLE FIELDS
# ==========================================================

def update_jobs(job_id, **kwargs):

    with LOCK:

        if job_id not in JOBS:
            return False

        JOBS[job_id].update(kwargs)

    return True

# ==========================================================
# DELETE JOB
# ==========================================================

def delete_job(job_id):

    with LOCK:
        JOBS.pop(job_id, None)

# ==========================================================
# EXISTS
# ==========================================================

def job_exists(job_id):

    with LOCK:
        return job_id in JOBS

# ==========================================================
# COUNT
# ==========================================================

def total_jobs():

    with LOCK:
        return len(JOBS)

# ==========================================================
# DEBUG
# ==========================================================

def get_all_jobs():

    with LOCK:
        return JOBS.copy()

# ==========================================================
# CLEANUP OLD JOBS
# ==========================================================

def cleanup_old_jobs(max_age=3600):

    now = time.time()

    with LOCK:

        expired = [
            job_id
            for job_id, job in JOBS.items()
            if now - job.get("created_at", now) > max_age
        ]

        for job_id in expired:
            del JOBS[job_id]

    return len(expired)
