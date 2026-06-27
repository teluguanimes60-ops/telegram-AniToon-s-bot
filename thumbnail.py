import os
import tempfile
import subprocess

from db import (
    save_thumbnail,
    get_thumbnail as db_get_thumbnail
)


async def save_thumb(user_id, file_id):
    await save_thumbnail(user_id, file_id)


async def get_thumb(client=None,
                    user_id=None,
                    mode="auto",
                    auto_path=None):

    if mode == "none":
        return None

    # --------------------------
    # Custom Thumbnail
    # --------------------------
    if mode == "saved":

        if not client:
            return None

        file_id = await db_get_thumbnail(user_id)

        if not file_id:
            return None

        tmp = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        )

        tmp.close()

        await client.download_media(
            file_id,
            file_name=tmp.name
        )

        return tmp.name

    # --------------------------
    # Auto Thumbnail
    # --------------------------
    if mode == "auto":

        if not auto_path:
            return None

        return generate_auto_thumb(auto_path)

    return None


def generate_auto_thumb(video):

    if not os.path.exists(video):
        return None

    thumb = video + "_thumb.jpg"

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        "00:00:03",
        "-i",
        video,
        "-frames:v",
        "1",
        thumb
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(thumb):
        return thumb

    return None
