# ==========================================
# AniToon Bot - PRO JOB ENGINE (FIXED)
# ==========================================

import uuid
import time

jobs = {}

# ---------------- CREATE JOB ----------------
def create_job(user_id, file_msg, mode="rename"):
    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        # BASIC INFO
        "job_id": job_id,
        "user_id": user_id,
        "file_msg": file_msg,
        "mode": mode,  # rename / convert

        # FILE DATA
        "file_path": None,
        "output_path": None,
        "new_name": None,

        # CONTROL SYSTEM
        "status": "waiting",  # waiting / downloading / processing / uploading / done
        "control": "run",     # run / pause / cancel

        # THUMBNAIL
        "thumb_mode": None,   # saved / auto / none
        "thumb_path": None,

        # CONVERT OPTIONS
        "convert_type": None,  # video / file

        # PROGRESS DATA
        "downloaded": 0,
        "uploaded": 0,
        "total_size": 0,

        # TIME TRACKING
        "start_time": time.time(),

        # MESSAGE REFERENCE
        "status_message": None,

        # FLAGS
        "finished": False,
        "error": None
    }

    return job_id


# ---------------- GET JOB ----------------
def get_job(job_id):
    return jobs.get(job_id)


# ---------------- DELETE JOB ----------------
def delete_job(job_id):
    if job_id in jobs:
        del jobs[job_id]


# ---------------- CONTROL FUNCTIONS ----------------
def pause_job(job_id):
    if job_id in jobs:
        jobs[job_id]["control"] = "pause"


def resume_job(job_id):
    if job_id in jobs:
        jobs[job_id]["control"] = "run"


def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]["control"] = "cancel"


def is_paused(job_id):
    return jobs.get(job_id, {}).get("control") == "pause"


def is_cancelled(job_id):
    return jobs.get(job_id, {}).get("control") == "cancel"


# ---------------- STATUS UPDATE ----------------
def set_status(job_id, status):
    if job_id in jobs:
        jobs[job_id]["status"] = status


def get_status(job_id):
    return jobs.get(job_id, {}).get("status")


# ---------------- FILE PATH ----------------
def set_file_path(job_id, path):
    if job_id in jobs:
        jobs[job_id]["file_path"] = path


def get_file_path(job_id):
    return jobs.get(job_id, {}).get("file_path")


# ---------------- OUTPUT PATH ----------------
def set_output_path(job_id, path):
    if job_id in jobs:
        jobs[job_id]["output_path"] = path


def get_output_path(job_id):
    return jobs.get(job_id, {}).get("output_path")


# ---------------- THUMBNAIL ----------------
def set_thumb(job_id, mode, path=None):
    if job_id in jobs:
        jobs[job_id]["thumb_mode"] = mode
        jobs[job_id]["thumb_path"] = path


def get_thumb(job_id):
    job = jobs.get(job_id)
    if not job:
        return None
    return job.get("thumb_path")


# ---------------- CONVERT TYPE ----------------
def set_convert_type(job_id, ctype):
    if job_id in jobs:
        jobs[job_id]["convert_type"] = ctype


def get_convert_type(job_id):
    return jobs.get(job_id, {}).get("convert_type")


# ---------------- PROGRESS UPDATE ----------------
def update_progress(job_id, downloaded=None, uploaded=None, total=None):
    if job_id not in jobs:
        return

    if downloaded is not None:
        jobs[job_id]["downloaded"] = downloaded

    if uploaded is not None:
        jobs[job_id]["uploaded"] = uploaded

    if total is not None:
        jobs[job_id]["total_size"] = total


def get_progress(job_id):
    job = jobs.get(job_id)
    if not job:
        return None

    return {
        "downloaded": job["downloaded"],
        "uploaded": job["uploaded"],
        "total": job["total_size"]
    }


# ---------------- FINISH ----------------
def finish_job(job_id):
    if job_id in jobs:
        jobs[job_id]["finished"] = True
        jobs[job_id]["status"] = "done"


# ---------------- ERROR ----------------
def set_error(job_id, error):
    if job_id in jobs:
        jobs[job_id]["error"] = str(error)
        jobs[job_id]["status"] = "error"