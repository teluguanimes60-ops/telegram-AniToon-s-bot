import os
import requests
import tarfile

FF_DIR = "ffmpeg_bin"
FFMPEG_PATH = f"{FF_DIR}/ffmpeg"

# ---------------- DOWNLOAD + SETUP FFMPEG ----------------
def setup_ffmpeg():
    # already ready
    if os.path.exists(FFMPEG_PATH):
        return

    print("⚙️ Setting up FFmpeg...")

    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

    # download file
    r = requests.get(url, stream=True)
    with open("ffmpeg.tar.xz", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    # extract
    with tarfile.open("ffmpeg.tar.xz") as tar:
        tar.extractall()

    # find extracted folder and rename
    for folder in os.listdir():
        if folder.startswith("ffmpeg") and os.path.isdir(folder):
            if os.path.exists(FF_DIR):
                os.system(f"rm -rf {FF_DIR}")
            os.rename(folder, FF_DIR)
            break

    print("✅ FFmpeg ready")


# ---------------- THUMBNAIL GENERATOR ----------------
def generate_thumbnail(video_path):
    setup_ffmpeg()

    thumb_path = "thumb.jpg"

    os.system(
        f"{FFMPEG_PATH} -y -i \"{video_path}\" "
        f"-ss 00:00:01 -vframes 1 \"{thumb_path}\""
    )

    if os.path.exists(thumb_path):
        return thumb_path
    return None
