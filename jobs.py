# ==========================================
# AniToon Bot - JOB SYSTEM (PRODUCTION FIXED)
# ==========================================

import time
import threading

# ---------------- MEMORY STORE ----------------
JOBS = {}
LOCK = threading.Lock()

# ==========================================
# 🚀 CREATE JOB
# ==========================================
def create_job(job_id, uid, data=None):

    if data is None:
        data = {}

    with LOCK:
        JOBS[job_id] = {
            "job_id": job_id,
            "uid": uid,
            "status": "pending",
            "created_at": time.time(),

            # default fields (prevents crash)
            "file_path": None,
            "new_name": None,
            "mode": "rename",
            "thumb_mode": "auto",

            **data
        }

    return JOBS[job_id]


# ==========================================
# 🔍 GET JOB (SAFE)
# ==========================================
def get_job(job_id):

    with LOCK:
        job = JOBS.get(job_id)

    if not job:
        return {
            "job_id": job_id,
            "uid": 0,
            "status": "missing",
            "file_path": None,
            "new_name": None,
            "mode": "rename",
            "thumb_mode": "auto"
        }

    return job


# ==========================================
# ✏️ UPDATE JOB (SAFE PATCH)
# ==========================================
def update_job(job_id, key, value):

    with LOCK:
        if job_id not in JOBS:
            JOBS[job_id] = {
                "job_id": job_id,
                "uid": 0
            }

        JOBS[job_id][key] = value


# ==========================================
# ❌ DELETE JOB
# ==========================================
def delete_job(job_id):

    with LOCK:
        if job_id in JOBS:
            del JOBS[job_id]


# ==========================================
# 📊 GET ALL JOBS (DEBUG)
# ==========================================
def get_all_jobs():
    with LOCK:
        return dict(JOBS)
