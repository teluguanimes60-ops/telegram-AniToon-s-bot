# ===========================
# AniToon Bot V2 - States
# ===========================

# Stores user states
# Example:
# {
#   123456789: {
#       "mode": "rename",
#       "step": "name",
#       "file": Message
#   }
# }

user_states = {}


def set_state(user_id, **kwargs):
    """
    Create or update a user's state.
    """
    if user_id not in user_states:
        user_states[user_id] = {}

    user_states[user_id].update(kwargs)


def get_state(user_id):
    """
    Get a user's current state.
    """
    return user_states.get(user_id, {})


def clear_state(user_id):
    """
    Remove a user's state after completion/cancel.
    """
    if user_id in user_states:
        del user_states[user_id]


def has_state(user_id):
    """
    Check whether a user currently has an active state.
    """
    return user_id in user_states
