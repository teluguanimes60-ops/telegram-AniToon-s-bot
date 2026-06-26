# ==========================================
# AniToon Bot - THUMBNAIL SYSTEM (PRODUCTION)
# ==========================================

import os
import subprocess

from db import (
    save_thumbnail,
    get_thumbnail as db_get_thumbnail
)

# ==========================================
# SAVE USER THUMBNAIL
# ==========================================
async def save_thumb(user_id: int, file_id: str):
    await save_thumbnail(user_id, file_id)


# ==========================================
# GET THUMBNAIL
# ==========================================
async def get_thumb(
    user_id=None,
    mode="auto",
    auto_path=None
):

    try:

        # ---------------- NONE ----------------
        if mode == "none":
            return None

        # ---------------- SAVED ----------------
        if mode == "saved":

            if not user_id:
                return None

            thumb = await db_get_thumbnail(user_id)

            if thumb and os.path.exists(thumb):
                return thumb

            return None

        # ---------------- AUTO ----------------
        if mode == "auto":

            if auto_path is None:
                return None

            return generate_auto_thumb(auto_path)

        return None

    except Exception as e:
        print("Thumbnail Error:", e)
        return None


# ==========================================
# AUTO THUMBNAIL
# ==========================================
def generate_auto_thumb(video_path):

    if not os.path.exists(video_path):
        return None

    thumb = video_path + "_thumb.jpg"

    if os.path.exists(thumb):
        try:
            os.remove(thumb)
        except:
            pass

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        "00:00:01",
        "-i",
        video_path,
        "-frames:v",
        "1",
        thumb,
    ]

    try:

        subprocess.run(
            cmd,
            check=True
        )

        if os.path.exists(thumb):
            return thumb

    except Exception as e:
        print("FFmpeg Thumbnail Error:", e)

    return None


# ==========================================
# CLEAN GENERATED THUMBNAIL
# ==========================================
def delete_auto_thumb(path):

    try:

        if path and os.path.exists(path):
            os.remove(path)

    except:
        pass
