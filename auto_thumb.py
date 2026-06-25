import os
import subprocess

FFMPEG_PATH = "ffmpeg"


def setup_ffmpeg():
    global FFMPEG_PATH

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        FFMPEG_PATH = "ffmpeg"
    except:
        FFMPEG_PATH = "ffmpeg"


def generate_thumbnail(video_path):
    try:
        thumb_path = f"thumb_{os.path.basename(video_path)}.jpg"

        subprocess.run(
            [
                FFMPEG_PATH,
                "-ss", "00:00:05",
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
