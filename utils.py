# ==========================================
# AniToon Bot - PRO UTILITIES ENGINE
# ==========================================

import os
import shutil
import subprocess

from thumbnail import get_thumb
from auto_thumb import generate_thumbnail


# ---------------- FILE TYPE DETECTION ----------------
def get_file_type(message):
    """
    Returns: video / document / audio / unknown
    """

    if message.video:
        return "video"

    if message.document:
        return "document"

    if message.audio:
        return "audio"

    return "unknown"


# ---------------- FILE NAME DETECTION ----------------
def get_file_name(message):
    """
    Extract original filename safely
    """

    if message.document and message.document.file_name:
        return message.document.file_name

    if message.video and message.video.file_name:
        return message.video.file_name

    if message.audio and message.audio.file_name:
        return message.audio.file_name

    return "file"


# ---------------- GET EXTENSION ----------------
def get_extension(filename):
    """
    Extract file extension safely
    """

    if not filename:
        return ""

    return os.path.splitext(filename)[1]


# ---------------- SAFE RENAME ----------------
def make_new_name(old_name, new_name):
    """
    Ensures extension is preserved
    """

    ext = get_extension(old_name)

    if "." in new_name:
        return new_name

    return new_name + ext


# ---------------- RENAME FILE ----------------
def rename_file(old_path, new_path):
    """
    Safe rename/move operation
    """

    try:
        shutil.move(old_path, new_path)
        return new_path
    except Exception:
        return old_path


# ---------------- THUMBNAIL HANDLER ----------------
def get_thumbnail(video_path, mode):
    """
    mode:
    - saved
    - auto
    - none
    """

    try:
        if mode == "saved":
            return get_thumb()

        if mode == "auto":
            return generate_thumbnail(video_path)

    except Exception:
        return None

    return None


# ---------------- CONVERT TO MP4 ----------------
def convert_to_mp4(input_file):
    """
    Stable ffmpeg conversion
    """

    output = os.path.splitext(input_file)[0] + ".mp4"

    cmd = [
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
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if os.path.exists(output):
            return output

    except Exception:
        pass

    return input_file


# ---------------- SAFE DELETE ----------------
def safe_delete(path):
    """
    Prevents crash on file deletion
    """

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass


# ---------------- FILE SIZE FORMAT ----------------
def human_size(size):
    """
    Converts bytes to readable format
    """

    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]

    while size > power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"