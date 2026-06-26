# states.py (PRO STATE ENGINE FIX)

# ===========================
# Central User State Manager
# ===========================

user_states = {}


# ---------------- SET STATE ----------------

def set_state(user_id, **kwargs):
    """
    Create or update user state safely
    """

    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id].update(kwargs)


# ---------------- GET STATE ----------------

def get_state(user_id):
    """
    Get current user state
    """

    return user_states.get(user_id, {})


# ---------------- CLEAR STATE ----------------

def clear_state(user_id):
    """
    Remove user state completely
    """

    if user_id in user_states:
        del user_states[user_id]


# ---------------- CHECK STATE ----------------

def has_state(user_id):
    """
    Check if user has active session
    """

    return user_id in user_states


# ---------------- RESET STEP ----------------

def reset_step(user_id):
    """
    Reset only step (not full state)
    Useful for multi-step flows
    """

    if user_id in user_states:
        user_states[user_id]["step"] = None


# ---------------- GET MODE ----------------

def get_mode(user_id):
    """
    Quick helper to get current mode
    """

    return user_states.get(user_id, {}).get("mode")