# ==========================================================
# 🤖 AniToon Bot - User State Engine (Production V7)
# ==========================================================

import time

# ==========================================================
# USER STATES
# ==========================================================

USER_STATES = {}

# ==========================================================
# DEFAULT
# ==========================================================

DEFAULT_STATE = {
    "mode": None,
    "step": None,
    "status": "idle",

    "rename_to": None,
    "convert_mode": None,

    "thumb_mode": "auto",
    "thumb_file_id": None,

    "processing": False,
    "paused": False,
    "cancelled": False,

    "queue": False,

    "progress_message": None,
    "original_message": None,

    "job_id": None,

    "created": 0
}

# ==========================================================
# CREATE
# ==========================================================

def create_state(user_id):

    state = DEFAULT_STATE.copy()

    state["created"] = time.time()

    USER_STATES[user_id] = state

    return state

# ==========================================================
# GET
# ==========================================================

def get_state(user_id):

    if user_id not in USER_STATES:
        create_state(user_id)

    return USER_STATES[user_id]

# ==========================================================
# UPDATE
# ==========================================================

def update_state(user_id, **kwargs):

    state = get_state(user_id)

    state.update(kwargs)

    return state

# ==========================================================
# BOT COMPATIBILITY
# ==========================================================

def set_state(user_id, **kwargs):
    return update_state(user_id, **kwargs)


def clear_state(user_id):

    USER_STATES.pop(user_id, None)

    create_state(user_id)

# ==========================================================
# MODE
# ==========================================================

def set_mode(user_id, mode):
    update_state(user_id, mode=mode)


def get_mode(user_id):
    return get_state(user_id)["mode"]

# ==========================================================
# STEP
# ==========================================================

def set_step(user_id, step):
    update_state(user_id, step=step)


def get_step(user_id):
    return get_state(user_id)["step"]

# ==========================================================
# JOB
# ==========================================================

def set_job(user_id, job_id):
    update_state(user_id, job_id=job_id)


def get_job(user_id):
    return get_state(user_id)["job_id"]

# ==========================================================
# RENAME
# ==========================================================

def set_rename(user_id, name):
    update_state(user_id, rename_to=name)


def get_rename(user_id):
    return get_state(user_id)["rename_to"]

# ==========================================================
# CONVERT
# ==========================================================

def set_convert(user_id, mode):
    update_state(user_id, convert_mode=mode)


def get_convert(user_id):
    return get_state(user_id)["convert_mode"]

# ==========================================================
# THUMBNAIL
# ==========================================================

def set_thumb_mode(user_id, mode):
    update_state(user_id, thumb_mode=mode)


def get_thumb_mode(user_id):
    return get_state(user_id)["thumb_mode"]

# ==========================================================
# PROCESS
# ==========================================================

def start_processing(user_id):

    update_state(
        user_id,
        processing=True,
        paused=False,
        cancelled=False,
        status="processing"
    )


def finish_processing(user_id):

    update_state(
        user_id,
        processing=False,
        paused=False,
        cancelled=False,
        status="completed"
    )


def pause_processing(user_id):

    update_state(
        user_id,
        paused=True,
        status="paused"
    )


def resume_processing(user_id):

    update_state(
        user_id,
        paused=False,
        status="processing"
    )


def cancel_processing(user_id):

    update_state(
        user_id,
        cancelled=True,
        processing=False,
        status="cancelled"
    )

# ==========================================================
# FLAGS
# ==========================================================

def is_processing(user_id):
    return get_state(user_id)["processing"]


def is_paused(user_id):
    return get_state(user_id)["paused"]


def is_cancelled(user_id):
    return get_state(user_id)["cancelled"]

# ==========================================================
# QUEUE
# ==========================================================

def set_queue(user_id, value=True):
    update_state(user_id, queue=value)


def in_queue(user_id):
    return get_state(user_id)["queue"]

# ==========================================================
# MESSAGES
# ==========================================================

def set_progress_message(user_id, msg):
    update_state(user_id, progress_message=msg)


def get_progress_message(user_id):
    return get_state(user_id)["progress_message"]


def set_original_message(user_id, msg):
    update_state(user_id, original_message=msg)


def get_original_message(user_id):
    return get_state(user_id)["original_message"]

# ==========================================================
# CLEANUP
# ==========================================================

def cleanup_old_states(max_age=86400):

    now = time.time()

    deleted = 0

    for uid in list(USER_STATES.keys()):

        if now - USER_STATES[uid]["created"] > max_age:

            USER_STATES.pop(uid)

            deleted += 1

    return deleted

# ==========================================================
# DEBUG
# ==========================================================

def total_states():
    return len(USER_STATES)


def get_all_states():
    return USER_STATES
