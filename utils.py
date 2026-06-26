# utils.py (PRO FIXED VERSION)

import os
import shutil
import subprocess

from thumbnail import get_thumb
from auto_thumb import generate_thumbnail


# ---------------- FILE INFO ----------------

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


# ---------------- RENAME ----------------

def make_new_name(old_name, new_name):
    """
    Safe rename with extension handling
    """

    ext = get_extension(old_name)

    if "." in new_name:
        return new_name

    return new_name + ext


def rename_file(old_path, new_path):
    """
    Safe file rename
    """
    try:
        shutil.move(old_path, new_path)
        return new_path
    except Exception:
        return old_path


# ---------------- THUMBNAIL ----------------

def get_thumbnail(file_path, mode):
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
            return generate_thumbnail(file_path)

        return None
    except:
        return None


# ---------------- CONVERT ----------------

def convert_to_mp4(input_file):
    """
    Safe ffmpeg conversion
    """

    output = os.path.splitext(input_file)[0] + "_converted.mp4"

    try:
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

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(output):
            return output

        return input_file

    except:
        return input_file


# ---------------- FILE SIZE ----------------

def human_size(size):

    power = 1024
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]

    while size > power and n < len(units) - 1:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


# ---------------- SAFE DELETE ----------------

def safe_delete(path):

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass