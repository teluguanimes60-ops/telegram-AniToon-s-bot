import os
import shutil
import subprocess

from thumbnail import get_thumb
from auto_thumb import generate_thumbnail


# =========================
# FILE NAME HELPERS
# =========================

def get_file_name(message):
    if message.document:
        return message.document.file_name

    if message.video:
        return message.video.file_name or "video.mp4"

    if message.audio:
        return message.audio.file_name or "audio.mp3"

    return "file"


def get_extension(filename):
    return os.path.splitext(filename)[1]


def make_new_name(old_name, new_name):
    """
    Attach extension safely
    """
    ext = get_extension(old_name)

    if "." in new_name:
        return new_name

    return new_name + ext


# =========================
# THUMBNAIL HANDLER
# =========================

def get_thumbnail(video_path, mode):
    """
    mode:
    saved → saved thumb
    auto  → ffmpeg thumb
    none  → no thumb
    """

    if mode == "saved":
        return get_thumb()

    if mode == "auto":
        return generate_thumbnail(video_path)

    return None


# =========================
# CONVERT TO MP4
# =========================

def convert_to_mp4(input_file):

    output = os.path.splitext(input_file)[0] + ".mp4"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_file,
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-c:a",
                "aac",
                output
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(output):
            return output

    except:
        pass

    return input_file


# =========================
# RENAME FILE
# =========================

def rename_file(old_path, new_path):
    """
    Safe rename / move
    """
    try:
        shutil.move(old_path, new_path)
        return new_path
    except:
        return old_path


# =========================
# HUMAN READABLE SIZE
# =========================

def human_size(size):

    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]

    while size > power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


# =========================
# SAFE DELETE
# =========================

def safe_delete(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass
