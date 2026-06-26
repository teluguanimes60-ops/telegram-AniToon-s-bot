# utils.py

import os
import shutil
import subprocess

from thumbnail import get_thumb
from auto_tumb import generate_thumbnail


# ---------------- FILE NAME ----------------

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
    ext = get_extension(old_name)

    if "." in new_name:
        return new_name

    return new_name + ext


# ---------------- THUMBNAIL ----------------

def get_thumbnail(video_path, mode):
    """
    mode:
    saved
    auto
    none
    """

    if mode == "saved":
        return get_thumb()

    if mode == "auto":
        return generate_thumbnail(video_path)

    return None


# ---------------- CONVERT ----------------

def convert_to_mp4(input_file):

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

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if os.path.exists(output):
        return output

    return input_file


# ---------------- COPY ----------------

def rename_file(old_path, new_path):

    shutil.move(old_path, new_path)

    return new_path


# ---------------- SIZE ----------------

def human_size(size):

    power = 1024

    n = 0

    units = ["B", "KB", "MB", "GB", "TB"]

    while size > power and n < 4:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


# ---------------- CLEAN ----------------

def safe_delete(path):

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass
