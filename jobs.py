# ==========================================================
# 🤖 AniToon Bot - Job Manager (Production v5)
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
    "status": "waiting",

    "mode": "rename",

    "new_name": None,

    "convert_to": None,

    "thumb_mode": "auto",

    "file_path": None,

    "output_path": None,

    "progress": 0,

    "queue_position": 0,

    "paused": False,

    "cancelled": False,

    "started": False,

    "finished": False
}

# ==========================================================
# CREATE
# ==========================================================

def create_job(job_id, uid, data=None):

    if data is None:
        data = {}

    with LOCK:

        # Prevent duplicate active jobs
        for job in JOBS.values():
            if job["uid"] == uid and not job.get("finished", False):
                return None

        job = DEFAULT_JOB.copy()

        job.update({
            "job_id": job_id,
            "uid": uid,
            "created_at": time.time()
        })

        job.update(data)

        JOBS[job_id] = job

        return job

# ==========================================================
# GET
# ==========================================================

def get_job(job_id):

    with LOCK:
        return JOBS.get(job_id)

# ==========================================================
# USER JOB
# ==========================================================

def get_user_job(uid):

    with LOCK:

        for job in JOBS.values():

            if job["uid"] == uid and not job.get("finished"):

                return job

    return None

# ==========================================================
# EXISTS
# ==========================================================

def job_exists(job_id):

    with LOCK:
        return job_id in JOBS

# ==========================================================
# UPDATE FIELD
# ==========================================================

def update_job(job_id, key, value):

    with LOCK:

        if job_id not in JOBS:
            return False

        JOBS[job_id][key] = value

        return True

# ==========================================================
# UPDATE MANY
# ==========================================================

def update_jobs(job_id, **kwargs):

    with LOCK:

        if job_id not in JOBS:
            return False

        JOBS[job_id].update(kwargs)

        return True

# ==========================================================
# PAUSE
# ==========================================================

def pause_job(job_id):

    return update_job(job_id, "paused", True)

# ==========================================================
# RESUME
# ==========================================================

def resume_job(job_id):

    return update_job(job_id, "paused", False)

# ==========================================================
# CANCEL
# ==========================================================

def cancel_job(job_id):

    return update_job(job_id, "cancelled", True)

# ==========================================================
# START
# ==========================================================

def start_job(job_id):

    return update_jobs(
        job_id,
        started=True,
        status="downloading"
    )

# ==========================================================
# FINISH
# ==========================================================

def finish_job(job_id):

    return update_jobs(
        job_id,
        finished=True,
        status="completed",
        progress=100
    )

# ==========================================================
# DELETE
# ==========================================================

def delete_job(job_id):

    with LOCK:

        JOBS.pop(job_id, None)

# ==========================================================
# TOTAL
# ==========================================================

def total_jobs():

    with LOCK:
        return len(JOBS)

# ==========================================================
# ACTIVE USERS
# ==========================================================

def active_users():

    with LOCK:

        return len({

            job["uid"]

            for job in JOBS.values()

            if not job.get("finished")
        })

# ==========================================================
# ALL JOBS
# ==========================================================

def get_all_jobs():

    with LOCK:

        return JOBS.copy()

# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_old_jobs(max_age=3600):

    now = time.time()

    removed = 0

    with LOCK:

        for job_id in list(JOBS.keys()):

            job = JOBS[job_id]

            if now - job.get("created_at", now) > max_age:

                del JOBS[job_id]

                removed += 1

    return removed
