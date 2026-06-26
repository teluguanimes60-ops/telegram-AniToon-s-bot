# thumbnail.py (PRO LEVEL FIXED)

import os

THUMB_FILE = "saved_thumbnail.jpg"


# ---------------- SAVE THUMBNAIL ----------------

def save_thumb(path):
    """
    Save user thumbnail safely
    """

    try:
        if not path:
            return False

        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)

        os.rename(path, THUMB_FILE)
        return True

    except Exception:
        return False


# ---------------- GET SAVED THUMB ----------------

def get_thumb():
    """
    Return saved thumbnail if exists
    """

    try:
        if os.path.exists(THUMB_FILE):
            return THUMB_FILE
        return None
    except:
        return None


# ---------------- DELETE THUMB ----------------

def delete_thumb():
    """
    Remove saved thumbnail
    """

    try:
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)
        return True
    except:
        return False


# ---------------- VALIDATE THUMB ----------------

def is_valid_thumb():
    """
    Check if thumbnail exists and is usable
    """

    try:
        return os.path.exists(THUMB_FILE) and os.path.getsize(THUMB_FILE) > 0
    except:
        return False


# ---------------- AUTO FALLBACK ----------------

def get_best_thumb(auto_thumb_func=None, video_path=None, mode="none"):
    """
    SMART thumbnail system (PRO LEVEL)

    mode:
    - saved
    - auto
    - none
    """

    try:

        # 1. Saved thumbnail (highest priority)
        if mode == "saved":
            if is_valid_thumb():
                return THUMB_FILE

        # 2. Auto thumbnail from video
        if mode == "auto" and video_path and auto_thumb_func:
            thumb = auto_thumb_func(video_path)
            if thumb and os.path.exists(thumb):
                return thumb

        # 3. No thumbnail
        return None

    except:
        return None