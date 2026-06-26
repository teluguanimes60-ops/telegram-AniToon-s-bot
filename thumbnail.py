# ==========================================
# AniToon Bot - THUMBNAIL SYSTEM (MONGO V4)
# ==========================================

import os
from db import save_thumbnail, get_thumbnail as db_get_thumb

# ==========================================
# 🖼 SAVE THUMBNAIL
# ==========================================
async def save_thumb(user_id: int, file_id: str):
    """
    Save thumbnail permanently in MongoDB
    """
    await save_thumbnail(user_id, file_id)

# ==========================================
# 📥 GET THUMBNAIL (MAIN FUNCTION)
# ==========================================
async def get_thumb(user_id: int = None, mode: str = "saved", auto_path: str = None):
    """
    Returns thumbnail based on mode:
    - saved → MongoDB thumbnail
    - auto → generate from video
    - none → None
    """

    try:

        # ❌ no thumbnail
        if mode == "none":
            return None

        # 📌 saved thumbnail from DB
        if mode == "saved" and user_id is not None:
            return await db_get_thumb(user_id)

        # ⚡ auto thumbnail from file
        if mode == "auto" and auto_path:

            return _generate_local_thumb(auto_path)

        return None

    except:
        return None

# ==========================================
# ⚡ AUTO THUMBNAIL GENERATOR (FFMPEG)
# ==========================================
def _generate_local_thumb(video_path: str):

    try:
        import subprocess

        thumb_path = f"{video_path}_thumb.jpg"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            thumb_path
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(thumb_path):
            return thumb_path

    except:
        pass

    return None
