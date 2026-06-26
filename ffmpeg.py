# ffmpeg.py (STABLE PRO VERSION)

import os
import shutil
import subprocess

FFMPEG_PATH = None


def find_ffmpeg():
    """
    Auto detect ffmpeg path for Render / Linux / local
    """

    global FFMPEG_PATH

    # Try system ffmpeg
    if shutil.which("ffmpeg"):
        FFMPEG_PATH = "ffmpeg"
        return FFMPEG_PATH

    # Common Render / Linux paths
    possible_paths = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            FFMPEG_PATH = path
            return FFMPEG_PATH

    # fallback (will still try system)
    FFMPEG_PATH = "ffmpeg"
    return FFMPEG_PATH


def get_ffmpeg():
    if not FFMPEG_PATH:
        find_ffmpeg()
    return FFMPEG_PATH