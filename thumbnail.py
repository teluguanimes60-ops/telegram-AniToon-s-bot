# ==========================
# AniToon Bot - PRO THUMBNAIL SYSTEM
# CLEAN + SAFE + STABLE
# ==========================

import os
import subprocess

THUMB_FILE = "saved_thumbnail.jpg"

FFMPEG = "ffmpeg"


# ---------------- SAVE THUMBNAIL ----------------

def save_thumb(path):
    """
    Save user thumbnail permanently
    """
    try:
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
    if os.path.exists(THUMB_FILE):
        return THUMB_FILE
    return None


# ---------------- AUTO THUMB (FROM VIDEO) ----------------

def generate_thumbnail(video_path):
    """
    Generate thumbnail from video using ffmpeg
    """

    try:
        if not video_path or not os.path.exists(video_path):
            return None

        thumb_path = f"thumb_{os.path.basename(video_path)}.jpg"

        cmd = [
            FFMPEG,
            "-y",
            "-ss", "00:00:02",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(thumb_path):
            return thumb_path

        return None

    except Exception:
        return None


# ---------------- GET FINAL THUMBNAIL ----------------

def get_final_thumbnail(mode, video_path=None):
    """
    Smart thumbnail selector:

    mode:
    - saved
    - auto
    - none
    """

    try:

        if mode == "saved":
            return get_thumb()

        elif mode == "auto":
            return generate_thumbnail(video_path)

        else:
            return None

    except:
        return None
