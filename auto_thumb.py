import os
import requests
import tarfile

FF_DIR = "ffmpeg_bin"
FFMPEG_PATH = f"{FF_DIR}/ffmpeg"

def setup_ffmpeg():
    if os.path.exists(FFMPEG_PATH):
        return

    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

    r = requests.get(url)
    open("ffmpeg.tar.xz", "wb").write(r.content)

    with tarfile.open("ffmpeg.tar.xz") as tar:
        tar.extractall()

    # find extracted folder
    for folder in os.listdir():
        if folder.startswith("ffmpeg") and os.path.isdir(folder):
            os.rename(folder, FF_DIR)
            break


def generate_thumbnail(video_path):
    setup_ffmpeg()

    thumb = "thumb.jpg"
    os.system(f"{FFMPEG_PATH} -i {video_path} -ss 00:00:01 -vframes 1 {thumb}")
    return thumb
