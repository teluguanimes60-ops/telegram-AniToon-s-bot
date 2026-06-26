import uuid

# =========================
# ACTIVE JOBS STORE
# =========================
jobs = {}


# =========================
# CREATE JOB
# =========================
def create_job(user_id, file_msg, mode="rename"):
    """
    Create a new processing job
    """

    job_id = str(uuid.uuid4())[:8]

    jobs[job_id] = {
        # identity
        "job_id": job_id,
        "user_id": user_id,

        # file
        "file_msg": file_msg,
        "file_path": None,

        # mode
        "mode": mode,  # rename / convert / instant

        # rename
        "new_name": None,

        # convert
        "convert_mode": None,

        # thumbnail
        "thumb_mode": None,
        "thumb_path": None,

        # control flags
        "paused": False,
        "cancelled": False,

        # progress tracking
        "downloaded": 0,
        "total": 0,

        # status message
        "status_message": None,

        # completion flag
        "finished": False
    }

    return job_id


# =========================
# GET JOB
# =========================
def get_job(job_id):
    return jobs.get(job_id)


# =========================
# DELETE JOB
# =========================
def delete_job(job_id):
    if job_id in jobs:
        del jobs[job_id]


# =========================
# CONTROL FUNCTIONS
# =========================
def pause_job(job_id):
    if job_id in jobs:
        jobs[job_id]["paused"] = True


def resume_job(job_id):
    if job_id in jobs:
        jobs[job_id]["paused"] = False


def cancel_job(job_id):
    if job_id in jobs:
        jobs[job_id]["cancelled"] = True


# =========================
# CHECK STATUS
# =========================
def is_paused(job_id):
    return jobs.get(job_id, {}).get("paused", False)


def is_cancelled(job_id):
    return jobs.get(job_id, {}).get("cancelled", False)


# =========================
# UPDATE STATUS MESSAGE
# =========================
def set_status(job_id, message):
    if job_id in jobs:
        jobs[job_id]["status_message"] = message


def get_status(job_id):
    return jobs.get(job_id, {}).get("status_message")


# =========================
# UPDATE FILE DATA
# =========================
def set_file_path(job_id, path):
    if job_id in jobs:
        jobs[job_id]["file_path"] = path


def get_file_path(job_id):
    return jobs.get(job_id, {}).get("file_path")


# =========================
# UPDATE PROGRESS
# =========================
def set_progress(job_id, downloaded, total):
    if job_id in jobs:
        jobs[job_id]["downloaded"] = downloaded
        jobs[job_id]["total"] = total


# =========================
# SET OPTIONS
# =========================
def set_new_name(job_id, name):
    if job_id in jobs:
        jobs[job_id]["new_name"] = name


def set_thumb_mode(job_id, mode):
    if job_id in jobs:
        jobs[job_id]["thumb_mode"] = mode


def set_convert_mode(job_id, mode):
    if job_id in jobs:
        jobs[job_id]["convert_mode"] = mode


# =========================
# FINISH JOB
# =========================
def finish_job(job_id):
    if job_id in jobs:
        jobs[job_id]["finished"] = True
