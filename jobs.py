# ==========================================
# AniToon Bot V2 - Jobs Manager
# ==========================================

import uuid

# Stores all active jobs
jobs = {}


def create_job(user_id, file_msg, mode="rename"):
    """
    Create a new job.
    """

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {

        # Basic
        "job_id": job_id,
        "user_id": user_id,
        "file_msg": file_msg,
        "mode": mode,

        # Rename
        "new_name": None,

        # Thumbnail
        "thumb_mode": None,

        # Convert
        "convert_mode": None,

        # Download Control
        "paused": False,
        "cancelled": False,

        # Progress
        "status_message": None,
        "downloaded": 0,
        "total": 0,

        # File Paths
        "download_path": None,
        "thumb_path": None,

        # Finished
        "finished": False
    }

    return job_id


def get_job(job_id):
    return jobs.get(job_id)


def delete_job(job_id):
    if job_id in jobs:
        del jobs[job_id]


def pause_job(job_id):
    if job_id in jobs:
        jobs[job_id]["paused"] = True


def resume_job(job_id):
    if job_id in jobs:
        jobs[job_id]["paused"] = False


def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]["cancelled"] = True


def is_paused(job_id):
    return jobs.get(job_id, {}).get("paused", False)


def is_cancelled(job_id):
    return jobs.get(job_id, {}).get("cancelled", False)


def set_status(job_id, message):
    if job_id in jobs:
        jobs[job_id]["status_message"] = message


def get_status(job_id):
    if job_id in jobs:
        return jobs[job_id]["status_message"]


def set_new_name(job_id, name):
    if job_id in jobs:
        jobs[job_id]["new_name"] = name


def set_thumb(job_id, mode):
    if job_id in jobs:
        jobs[job_id]["thumb_mode"] = mode


def set_convert(job_id, mode):
    if job_id in jobs:
        jobs[job_id]["convert_mode"] = mode


def set_download(job_id, current, total):
    if job_id in jobs:
        jobs[job_id]["downloaded"] = current
        jobs[job_id]["total"] = total


def set_download_path(job_id, path):
    if job_id in jobs:
        jobs[job_id]["download_path"] = path


def get_download_path(job_id):
    if job_id in jobs:
        return jobs[job_id]["download_path"]


def finish_job(job_id):
    if job_id in jobs:
        jobs[job_id]["finished"] = True
