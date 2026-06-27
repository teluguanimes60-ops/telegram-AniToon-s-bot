# ==========================================================
# 🤖 AniToon Bot - Auto Thumbnail Generator (Production v5)
# ==========================================================

import os
import subprocess

from ffmpeg import get_ffmpeg

# ==========================================================
# GENERATE AUTO THUMBNAIL
# ==========================================================

def generate_thumbnail(video_path, second=5):
    """
    Generate a thumbnail from a video.

    Returns:
        thumbnail_path
        or
        None
    """

    try:

        if not video_path:
            return None

        if not os.path.exists(video_path):
            return None

        thumb_path = os.path.splitext(video_path)[0] + "_thumb.jpg"

        # Remove old thumbnail
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except Exception:
                pass

        cmd = [
            get_ffmpeg(),
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-ss", str(second),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        if os.path.exists(thumb_path):
            return thumb_path

    except Exception as e:

        print("AUTO THUMB ERROR:", e)

    return None


# ==========================================================
# DELETE GENERATED THUMBNAIL
# ==========================================================

def delete_thumbnail(path):

    try:

        if path and os.path.exists(path):
            os.remove(path)

    except Exception:
        pass


# ==========================================================
# CHECK IMAGE
# ==========================================================

def thumbnail_exists(path):

    return bool(path and os.path.exists(path))
