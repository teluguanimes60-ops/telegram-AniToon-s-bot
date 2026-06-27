# ==========================================================
# 🤖 AniToon Bot - Utility Functions (Production v5)
# ==========================================================

import os
import uuid

# ==========================================================
# HUMAN FILE SIZE
# ==========================================================

def human_size(size):

    if not size:
        return "0 B"

    size = float(size)

    units = ["B", "KB", "MB", "GB", "TB"]

    i = 0

    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1

    return f"{size:.2f} {units[i]}"


# ==========================================================
# HUMAN TIME
# ==========================================================

def human_time(seconds):

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


# ==========================================================
# FILE NAME
# ==========================================================

def file_name(path):

    return os.path.basename(path)


# ==========================================================
# FILE EXTENSION
# ==========================================================

def file_ext(path):

    return os.path.splitext(path)[1]


# ==========================================================
# FILE NAME WITHOUT EXTENSION
# ==========================================================

def file_stem(path):

    return os.path.splitext(os.path.basename(path))[0]


# ==========================================================
# CHANGE FILE NAME
# ==========================================================

def rename_file(path, new_name):

    ext = file_ext(path)

    new_path = os.path.join(
        os.path.dirname(path),
        new_name + ext
    )

    os.rename(path, new_path)

    return new_path


# ==========================================================
# UNIQUE FILE NAME
# ==========================================================

def unique_name(ext=""):

    if ext and not ext.startswith("."):
        ext = "." + ext

    return f"{uuid.uuid4().hex}{ext}"


# ==========================================================
# SAFE DELETE
# ==========================================================

def safe_delete(path):

    try:

        if path and os.path.exists(path):

            os.remove(path)

    except Exception:
        pass


# ==========================================================
# CREATE DIRECTORY
# ==========================================================

def ensure_dir(path):

    os.makedirs(path, exist_ok=True)


# ==========================================================
# IS VIDEO
# ==========================================================

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v",
    ".ts",
    ".flv"
}

def is_video(path):

    return file_ext(path).lower() in VIDEO_EXTENSIONS


# ==========================================================
# IS AUDIO
# ==========================================================

AUDIO_EXTENSIONS = {
    ".mp3",
    ".aac",
    ".wav",
    ".flac",
    ".m4a",
    ".ogg"
}

def is_audio(path):

    return file_ext(path).lower() in AUDIO_EXTENSIONS


# ==========================================================
# IS IMAGE
# ==========================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

def is_image(path):

    return file_ext(path).lower() in IMAGE_EXTENSIONS
