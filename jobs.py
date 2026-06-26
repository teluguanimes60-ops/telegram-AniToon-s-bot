# ==========================
# AniToon Bot - PRO JOB SYSTEM
# CLEAN + STABLE VERSION
# ==========================

import uuid

jobs = {}

# ---------------- CREATE JOB ----------------

def create_job(user_id, file_msg, mode):
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        "job_id": job_id,
        "user_id": user_id,
        "file_msg": file_msg,

        # CORE
        "mode": mode,  # rename / convert / instant

        # FILE INFO
        "file_path": None,
        "file_type": None,  # video / document / audio

        # RENAME
        "new_name": None,

        # CONVERT
        "convert_type": None,  # video / file

        # THUMBNAIL
        "thumb_mode": "none",  # saved / auto / none
        "thumb_path": None,

        # CONTROL SYSTEM
        "status": "running",  # running / paused / cancelled

        # PROGRESS
        "downloaded": 0,
        "total": 0,

        # FINAL OUTPUT
        "output_path": None,

        # CLEAN STATE FLAG
        "done": False
    }

    return job_id


# ---------------- GET JOB ----------------

def get_job(job_id):
    return jobs.get(job_id)


# ---------------- UPDATE JOB ----------------

def update_job(job_id, **kwargs):
    if job_id in jobs:
        jobs[job_id].update(kwargs)


# ---------------- CONTROL ACTIONS ----------------

def pause_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "paused"


def resume_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "running"


def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]["status"] = "cancelled"


def is_paused(job_id):
    return jobs.get(job_id, {}).get("status") == "paused"


def is_cancelled(job_id):
    return jobs.get(job_id, {}).get("status") == "cancelled"


# ---------------- FILE PATH ----------------

def set_file_path(job_id, path):
    if job_id in jobs:
        jobs[job_id]["file_path"] = path


def get_file_path(job_id):
    return jobs.get(job_id, {}).get("file_path")


# ---------------- THUMBNAIL ----------------

def set_thumb(job_id, mode, path=None):
    if job_id in jobs:
        jobs[job_id]["thumb_mode"] = mode
        jobs[job_id]["thumb_path"] = path


def get_thumb(job_id):
    return jobs.get(job_id, {}).get("thumb_path")


# ---------------- PROGRESS ----------------

def set_progress(job_id, current, total):
    if job_id in jobs:
        jobs[job_id]["downloaded"] = current
        jobs[job_id]["total"] = total


# ---------------- OUTPUT ----------------

def set_output(job_id, path):
    if job_id in jobs:
        jobs[job_id]["output_path"] = path


# ---------------- FINISH ----------------

def finish_job(job_id):
    if job_id in jobs:
        jobs[job_id]["done"] = True
