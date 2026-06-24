import os

THUMB_PATH = "thumb.jpg"

def save_thumb(path):
    if os.path.exists(THUMB_PATH):
        os.remove(THUMB_PATH)
    os.rename(path, THUMB_PATH)

def get_thumb():
    return THUMB_PATH if os.path.exists(THUMB_PATH) else None
