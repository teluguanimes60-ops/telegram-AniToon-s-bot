# ===========================
# AniToon Bot - FFMPEG CONFIG
# ===========================

import os
import shutil

# default fallback path
FFMPEG_PATH = None


# ===========================
# INIT FFMPEG PATH
# ===========================
def init_ffmpeg():
    """
    Detect ffmpeg automatically in system.
    Works for Linux / Windows / Render / VPS
    """

    global FFMPEG_PATH

    # try system ffmpeg
    path = shutil.which("ffmpeg")

    if path:
        FFMPEG_PATH = path
    else:
        # fallback (assume installed in PATH)
        FFMPEG_PATH = "ffmpeg"

    return FFMPEG_PATH


# ===========================
# GET FFMPEG PATH
# ===========================
def get_ffmpeg():
    """
    Return safe ffmpeg path
    """

    global FFMPEG_PATH

    if not FFMPEG_PATH:
        init_ffmpeg()

    return FFMPEG_PATH
