# ==========================================================
# 🤖 AniToon Bot - Thumbnail Manager (Production v5)
# ==========================================================

import os

from db import (
    save_thumbnail,
    get_thumbnail
)

from auto_thumb import (
    generate_thumbnail,
    delete_thumbnail
)

# ==========================================================
# SAVE USER THUMBNAIL
# ==========================================================

async def save_thumb(user_id: int, file_id: str):
    """
    Save user's custom thumbnail.
    """
    await save_thumbnail(user_id, file_id)


# ==========================================================
# GET THUMBNAIL
# ==========================================================

async def get_thumb(
    user_id=None,
    mode="auto",
    auto_path=None
):
    """
    Modes:
        custom -> User's saved thumbnail
        auto   -> Generate automatically
        none   -> No thumbnail
    """

    try:

        # ---------------- NONE ----------------

        if mode == "none":
            return None

        # ---------------- CUSTOM ----------------

        if mode == "custom":

            if not user_id:
                return None

            thumb = await get_thumbnail(user_id)

            # Local image path
            if thumb and os.path.exists(thumb):
                return thumb

            # Telegram file_id
            if thumb:
                return thumb

            return None

        # ---------------- AUTO ----------------

        if mode == "auto":

            if not auto_path:
                return None

            return generate_thumbnail(auto_path)

        return None

    except Exception as e:

        print("THUMBNAIL ERROR:", e)

        return None


# ==========================================================
# CLEANUP AUTO THUMB
# ==========================================================

def cleanup_thumb(path):
    """
    Delete generated thumbnail after upload.
    """

    try:

        if path and os.path.exists(path):

            delete_thumbnail(path)

    except Exception:
        pass


# ==========================================================
# CHECK THUMB
# ==========================================================

def thumb_exists(path):

    return bool(path and os.path.exists(path))
