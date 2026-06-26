# ==========================
# AniToon Bot - PRO UTILS SYSTEM
# CLEAN + SAFE + STABLE CORE
# ==========================

import os
import shutil
import subprocess

from thumbnail import get_thumb, generate_thumbnail


# ---------------- FILE TYPE DETECTION ----------------

def get_file_type(message):
    """
    Detect file type from Telegram message
    """

    if message.video:
        return "video"

    if message.document:
        return "document"

    if message.audio:
        return "audio"

    return "unknown"


# ---------------- FILE NAME ----------------

def get_file_name(message):
    """
    Get original file name safely
    """

    if message.document:
        return message.document.file_name

    if message.video:
        return message.video.file_name or "video.mp4"

    if message.audio:
        return message.audio.file_name or "audio.mp3"

    return "file"


# ---------------- EXTENSION ----------------

def get_extension(filename):
    return os.path.splitext(filename)[1]


# ---------------- SAFE RENAME ----------------

def build_new_name(old_name, new_name):
    """
    Prevent double extension bugs
    """

    ext = get_extension(old_name)

    if not new_name:
        return old_name

    if "." in new_name:
        return new_name

    return new_name + ext


# ---------------- RENAME FILE ----------------

def rename_file(old_path, new_path):
    """
    Safe file rename/move
    """

    try:
        shutil.move(old_path, new_path)
        return new_path
    except Exception:
        return old_path


# ---------------- CONVERT TO MP4 ----------------

def convert_to_mp4(input_file):
    """
    Convert any video to mp4 using ffmpeg
    """

    try:
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

    except Exception:
        return input_file


# ---------------- SMART THUMBNAIL ----------------

def get_thumbnail(video_path, mode):
    """
    Unified thumbnail system
    """

    try:

        if mode == "saved":
            return get_thumb()

        if mode == "auto":
            return generate_thumbnail(video_path)

        return None

    except:
        return None


# ---------------- SAFE DELETE ----------------

def safe_delete(path):
    """
    Delete files safely
    """

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass


# ---------------- HUMAN SIZE ----------------

def human_size(size):
    """
    Convert bytes to readable format
    """

    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1

    return f"{size:.2f} {units[i]}"
