import os
import shutil
import subprocess

from thumbnail import get_thumb
from auto_thumb import generate_thumbnail


# ---------------- FILE INFO ----------------

def get_extension(filename):
    return os.path.splitext(filename)[1]


def make_new_name(old_name, new_name):
    ext = get_extension(old_name)

    if "." in new_name:
        return new_name

    return new_name + ext


# ---------------- RENAME ----------------

def rename_file(old_path, new_path):
    shutil.move(old_path, new_path)
    return new_path


# ---------------- THUMBNAIL ----------------

def get_thumbnail(video_path, mode):

    if mode == "saved":
        return get_thumb()

    if mode == "auto":
        return generate_thumbnail(video_path)

    return None


# ---------------- CONVERT ----------------

def convert_to_mp4(input_file):

    output = os.path.splitext(input_file)[0] + ".mp4"

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        output
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return output if os.path.exists(output) else input_file


# ---------------- CLEAN SAFE ----------------

def safe_delete(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except:
        pass
