# ==========================================================
# 🤖 AniToon Bot - FFmpeg Manager (Production v5)
# ==========================================================

import os
import shutil
import subprocess

# ==========================================================
# PATHS
# ==========================================================

FFMPEG = None
FFPROBE = None


# ==========================================================
# FIND EXECUTABLE
# ==========================================================

def _find_binary(name):

    path = shutil.which(name)

    if path:
        return path

    possible = [
        f"/usr/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/bin/{name}",
        name
    ]

    for p in possible:

        if os.path.exists(p):
            return p

    return name


# ==========================================================
# INITIALIZE
# ==========================================================

def setup_ffmpeg():

    global FFMPEG
    global FFPROBE

    FFMPEG = _find_binary("ffmpeg")
    FFPROBE = _find_binary("ffprobe")

    return FFMPEG


# ==========================================================
# GETTERS
# ==========================================================

def get_ffmpeg():

    global FFMPEG

    if FFMPEG is None:
        setup_ffmpeg()

    return FFMPEG


def get_ffprobe():

    global FFPROBE

    if FFPROBE is None:
        setup_ffmpeg()

    return FFPROBE


# ==========================================================
# CHECK INSTALLATION
# ==========================================================

def ffmpeg_exists():

    try:

        subprocess.run(
            [get_ffmpeg(), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        return True

    except Exception:

        return False


def ffprobe_exists():

    try:

        subprocess.run(
            [get_ffprobe(), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        return True

    except Exception:

        return False


# ==========================================================
# RUN COMMAND
# ==========================================================

def run(command):

    """
    Execute FFmpeg command.

    Returns:
        True  -> Success
        False -> Failed
    """

    try:

        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        return True

    except Exception as e:

        print("FFmpeg Error:", e)

        return False


# ==========================================================
# VIDEO INFO
# ==========================================================

def get_video_info(video_path):

    """
    Returns width, height and duration.

    Returns:
        {
            width,
            height,
            duration
        }

    Returns None on failure.
    """

    try:

        cmd = [
            get_ffprobe(),
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1",
            video_path
        ]

        result = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL
        ).decode()

        info = {}

        for line in result.splitlines():

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            info[key] = value

        return {
            "width": int(float(info.get("width", 0))),
            "height": int(float(info.get("height", 0))),
            "duration": int(float(info.get("duration", 0)))
        }

    except Exception:

        return None


# ==========================================================
# STARTUP
# ==========================================================

setup_ffmpeg()

print("FFmpeg :", get_ffmpeg())
print("FFprobe:", get_ffprobe())
print("FFmpeg Available :", ffmpeg_exists())
print("FFprobe Available:", ffprobe_exists())
