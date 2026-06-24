import os

def get_ffmpeg():
    for file in os.listdir():
        if file.startswith("ffmpeg") and os.path.isdir(file):
            return f"./{file}/ffmpeg"
    return "ffmpeg"

FFMPEG_PATH = get_ffmpeg()

def generate_thumbnail(video_path):
    thumb = "thumb.jpg"
    os.system(f"{FFMPEG_PATH} -i {video_path} -ss 00:00:01 -vframes 1 {thumb}")
    return thumb
