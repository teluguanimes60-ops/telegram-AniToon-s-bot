# ==========================================
# AniToon Bot - PRO THUMBNAIL SYSTEM
# ==========================================

import os

THUMB_FILE = "saved_thumbnail.jpg"


# ---------------- SAVE THUMBNAIL ----------------
def save_thumb(path):
    """
    Save user thumbnail (replace old one safely)
    """

    try:
        # delete old thumbnail if exists
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)

        # move new thumbnail
        os.rename(path, THUMB_FILE)

        return True

    except Exception:
        return False


# ---------------- GET SAVED THUMB ----------------
def get_thumb():
    """
    Return saved thumbnail if exists
    """

    if os.path.exists(THUMB_FILE):
        return THUMB_FILE

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
def is_thumb_available():
    """
    Check if thumbnail exists and is usable
    """

    return os.path.exists(THUMB_FILE)


# ---------------- SAFE THUMB SELECTOR ----------------
def get_safe_thumb(mode, auto_thumb_func=None, video_path=None):
    """
    Unified thumbnail system:

    mode:
    - saved → uses saved thumbnail
    - auto → generates from video
    - none → no thumbnail
    """

    if mode == "saved":
        return get_thumb()

    elif mode == "auto":
        try:
            if auto_thumb_func and video_path:
                return auto_thumb_func(video_path)
        except:
            return None

    return None