import os
import subprocess

FFMPEG_PATH = "ffmpeg"


# ---------------- INIT CHECK ----------------
def setup_ffmpeg():
    global FFMPEG_PATH

    try:
        subprocess.run(
            [FFMPEG_PATH, "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        FFMPEG_PATH = "ffmpeg"


# ---------------- THUMBNAIL GENERATOR ----------------
def generate_thumbnail(video_path):

    if not video_path or not os.path.exists(video_path):
        return None

    try:
        base = os.path.splitext(os.path.basename(video_path))[0]
        thumb_path = f"{base}_thumb.jpg"

        subprocess.run([
            FFMPEG_PATH,
            "-y",
            "-ss", "00:00:02",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )

        if os.path.exists(thumb_path):
            return thumb_path

        return None

    except Exception:
        return None
