import os
import tempfile
import subprocess

from db import (
    save_thumbnail,
    get_thumbnail as db_get_thumbnail
)


# ==========================================================
# SAVE THUMBNAIL
# ==========================================================

async def save_thumb(client, user_id, file_id):
    await save_thumbnail(user_id, file_id)
    return True


# ==========================================================
# GET THUMBNAIL
# ==========================================================

async def get_thumb(
    client=None,
    user_id=None,
    mode="auto",
    auto_path=None
):

    # No thumbnail
    if mode == "none":
        return None

    # -------------------------
    # Saved Thumbnail
    # -------------------------

    if mode == "saved":

        if client is None:
            return None

        file_id = await db_get_thumbnail(user_id)

        if not file_id:
            return None

        tmp = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        )
        tmp.close()

        try:
            await client.download_media(
                file_id=file_id,
                file_name=tmp.name
            )
        except Exception:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)
            return None

        return tmp.name

    # -------------------------
    # Auto Thumbnail
    # -------------------------

    if mode == "auto":

        if not auto_path:
            return None

        return generate_auto_thumb(auto_path)

    return None


# ==========================================================
# AUTO THUMBNAIL
# ==========================================================

def generate_auto_thumb(video_path):

    if not os.path.exists(video_path):
        return None

    thumb = video_path + "_thumb.jpg"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:03",
        "-i",
        video_path,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        thumb
    ]

    try:

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

    except Exception:
        return None

    if os.path.exists(thumb):
        return thumb

    return None


# ==========================================================
# DELETE AUTO THUMBNAIL
# ==========================================================

def delete_auto_thumb(path):

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
