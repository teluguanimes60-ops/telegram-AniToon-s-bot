import os
import subprocess

# Default ffmpeg command
FFMPEG_PATH = "ffmpeg"


# =========================
# SETUP FFMPEG
# =========================
def setup_ffmpeg():
    """
    Check if ffmpeg exists in system.
    If not found, fallback to default command.
    """

    global FFMPEG_PATH

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        FFMPEG_PATH = "ffmpeg"

    except Exception:
        FFMPEG_PATH = "ffmpeg"


# =========================
# GENERATE THUMBNAIL
# =========================
def generate_thumbnail(video_path):
    """
    Extract thumbnail from video at 5th second.
    """

    try:
        if not video_path or not os.path.exists(video_path):
            return None

        thumb_path = f"thumb_{os.path.basename(video_path)}.jpg"

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-ss", "00:00:05",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(thumb_path):
            return thumb_path

        return None

    except Exception:
        return None
