# ==========================================================
# 🤖 AniToon Bot - User State Engine (Project V5)
# ==========================================================

import time

# ==========================================================
# USER STATES
# ==========================================================

USER_STATES = {}

# ==========================================================
# DEFAULT STATE
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
# CREATE STATE
# ==========================================================

def create_state(user_id: int):

    USER_STATES[user_id] = DEFAULT_STATE.copy()

    USER_STATES[user_id]["created"] = time.time()

    return USER_STATES[user_id]

# ==========================================================
# GET STATE
# ==========================================================

def get_state(user_id: int):

    if user_id not in USER_STATES:
        create_state(user_id)

    return USER_STATES[user_id]

# ==========================================================
# UPDATE
# ==========================================================

def update_state(user_id: int, **kwargs):

    state = get_state(user_id)

    state.update(kwargs)

    return state

# ==========================================================
# SET MODE
# ==========================================================

def set_mode(user_id: int, mode: str):

    update_state(
        user_id,
        mode=mode
    )

# ==========================================================
# GET MODE
# ==========================================================

def get_mode(user_id: int):

    return get_state(user_id)["mode"]

# ==========================================================
# SET STEP
# ==========================================================

def set_step(user_id: int, step: str):

    update_state(
        user_id,
        step=step
    )

# ==========================================================
# GET STEP
# ==========================================================

def get_step(user_id: int):

    return get_state(user_id)["step"]

# ==========================================================
# START PROCESS
# ==========================================================

def start_processing(user_id: int):

    update_state(
        user_id,
        processing=True,
        status="processing",
        paused=False,
        cancelled=False
    )

# ==========================================================
# FINISH PROCESS
# ==========================================================

def finish_processing(user_id: int):

    update_state(
        user_id,
        processing=False,
        status="completed",
        paused=False
    )

# ==========================================================
# CANCEL
# ==========================================================

def cancel_processing(user_id: int):

    update_state(
        user_id,
        cancelled=True,
        processing=False,
        status="cancelled"
    )

# ==========================================================
# PAUSE
# ==========================================================

def pause_processing(user_id: int):

    update_state(
        user_id,
        paused=True,
        status="paused"
    )

# ==========================================================
# RESUME
# ==========================================================

def resume_processing(user_id: int):

    update_state(
        user_id,
        paused=False,
        status="processing"
    )

# ==========================================================
# CHECKS
# ==========================================================

def is_processing(user_id: int):

    return get_state(user_id)["processing"]


def is_paused(user_id: int):

    return get_state(user_id)["paused"]


def is_cancelled(user_id: int):

    return get_state(user_id)["cancelled"]

# ==========================================================
# RESET
# ==========================================================

def reset_state(user_id: int):

    if user_id in USER_STATES:
        del USER_STATES[user_id]

# ==========================================================
# CLEAN OLD STATES
# ==========================================================

def cleanup_old_states(max_age=86400):

    now = time.time()

    remove = []

    for uid, state in USER_STATES.items():

        if now - state.get("created", now) > max_age:

            remove.append(uid)

    for uid in remove:

        USER_STATES.pop(uid, None)

    return len(remove)

# ==========================================================
# TOTAL USERS
# ==========================================================

def total_states():

    return len(USER_STATES)

# ==========================================================
# DEBUG
# ==========================================================

def get_all_states():

    return USER_STATES
