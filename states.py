# ===========================
# AniToon Bot - STATES SYSTEM
# ===========================

# stores all user sessions
user_states = {}


# ===========================
# SET STATE
# ===========================
def set_state(user_id, **kwargs):
    """
    Create or update user state
    Example:
    set_state(123, mode="rename", step="name")
    """

    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id].update(kwargs)


# ===========================
# GET STATE
# ===========================
def get_state(user_id):
    """
    Return user state safely
    """
    return user_states.get(user_id, {})


# ===========================
# CLEAR STATE
# ===========================
def clear_state(user_id):
    """
    Remove user state after completion or cancel
    """
    if user_id in user_states:
        del user_states[user_id]


# ===========================
# CHECK STATE EXISTS
# ===========================
def has_state(user_id):
    """
    Check if user is in active session
    """
    return user_id in user_states


# ===========================
# UPDATE STEP
# ===========================
def set_step(user_id, step):
    """
    Update only step (file → name → done)
    """
    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id]["step"] = step


# ===========================
# UPDATE MODE
# ===========================
def set_mode(user_id, mode):
    """
    Set mode safely
    rename / convert / instant / thumb
    """
    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id]["mode"] = mode
