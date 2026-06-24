import subprocess
import os

def get_ffmpeg():
    for file in os.listdir():
        if file.startswith("ffmpeg") and os.path.isdir(file):
            return f"./{file}/ffmpeg"
    return "ffmpeg"

FFMPEG_PATH = get_ffmpeg()

def generate_thumbnail(video_path):
    thumb_path = video_path + ".jpg"

    try:
        # take frame at 2nd second
        cmd = [
            "ffmpeg",
            "-ss", "00:00:02",
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(thumb_path):
            return thumb_path
        else:
            return None

    except:
        return None
