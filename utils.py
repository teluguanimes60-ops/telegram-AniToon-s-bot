# ==========================================================
# 🤖 AniToon Bot - Utility Functions (Production V7)
# ==========================================================

import os
import uuid
import shutil

# ==========================================================
# HUMAN FILE SIZE
# ==========================================================

def human_size(size):

    size = float(size or 0)

    for unit in ["B", "KB", "MB", "GB", "TB"]:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


# ==========================================================
# HUMAN TIME
# ==========================================================

def human_time(seconds):

    seconds = max(int(seconds), 0)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"


# ==========================================================
# FILE HELPERS
# ==========================================================

def file_name(path):
    return os.path.basename(path)


def file_ext(path):
    return os.path.splitext(path)[1]


def file_stem(path):
    return os.path.splitext(file_name(path))[0]


# ==========================================================
# SAFE RENAME
# ==========================================================

def rename_file(path, new_name):

    ext = file_ext(path)

    folder = os.path.dirname(path)

    new_path = os.path.join(folder, new_name + ext)

    if os.path.abspath(path) == os.path.abspath(new_path):
        return path

    if os.path.exists(new_path):
        os.remove(new_path)

    shutil.move(path, new_path)

    return new_path


# ==========================================================
# UNIQUE NAME
# ==========================================================

def unique_name(ext=""):

    if ext and not ext.startswith("."):
        ext = "." + ext

    return uuid.uuid4().hex + ext


# ==========================================================
# SAFE DELETE
# ==========================================================

def safe_delete(path):

    try:

        if path and os.path.exists(path):

            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)

    except Exception:
        pass


# ==========================================================
# DIRECTORY
# ==========================================================

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ==========================================================
# FILE TYPES
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

AUDIO_EXTENSIONS = {
    ".mp3",
    ".aac",
    ".wav",
    ".ogg",
    ".flac",
    ".m4a"
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


def is_video(path):
    return file_ext(path).lower() in VIDEO_EXTENSIONS


def is_audio(path):
    return file_ext(path).lower() in AUDIO_EXTENSIONS


def is_image(path):
    return file_ext(path).lower() in IMAGE_EXTENSIONS


def is_document(path):
    return not (
        is_video(path)
        or is_audio(path)
        or is_image(path)
    )
