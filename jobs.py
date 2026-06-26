# ==========================================
# AniToon Bot - JOB SYSTEM (PRO FIXED)
# ==========================================

import uuid
import os

# ---------------- JOB STORE ----------------
jobs = {}

# ---------------- CREATE JOB ----------------
def create_job(uid, msg, mode):
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "id": job_id,
        "uid": uid,
        "file": msg,

        # core mode
        "mode": mode,  # rename / convert / instant

        # processing controls
        "status": "running",  # running / pause / cancel

        # rename
        "new_name": None,

        # convert
        "convert_type": None,

        # thumbnail
        "thumb_mode": None,  # saved / auto / none

        # output file
        "file_path": None
    }

    return job_id

# ---------------- GET JOB ----------------
def get_job(job_id):
    return jobs.get(job_id)

# ---------------- UPDATE JOB ----------------
def update_job(job_id, key, value):
    if job_id in jobs:
        jobs[job_id][key] = value

# ---------------- PAUSE ----------------
def pause_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "pause"

# ---------------- RESUME ----------------
def resume_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "running"

# ---------------- CANCEL ----------------
def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "cancel"

# ---------------- CHECK STATUS ----------------
def is_cancelled(job_id):
    return jobs.get(job_id, {}).get("status") == "cancel"

def is_paused(job_id):
    return jobs.get(job_id, {}).get("status") == "pause"

# ---------------- CLEAN JOB ----------------
def remove_job(job_id):
    if job_id in jobs:
        try:
            jobs.pop(job_id)
        except:
            pass

# ---------------- SET FILE PATH ----------------
def set_file(job_id, path):
    if job_id in jobs:
        jobs[job_id]["file_path"] = path

# ---------------- GET FILE PATH ----------------
def get_file(job_id):
    return jobs.get(job_id, {}).get("file_path")
