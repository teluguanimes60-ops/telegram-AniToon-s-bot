import os

THUMB_PATH = "thumb.jpg"

def save_thumb(file_path):
    if os.path.exists(THUMB_PATH):
        os.remove(THUMB_PATH)

    os.rename(file_path, THUMB_PATH)


def get_thumb():
    if os.path.exists(THUMB_PATH):
        return THUMB_PATH
    return None
