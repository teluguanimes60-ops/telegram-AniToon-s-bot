import os

THUMB_FILE = "saved_thumbnail.jpg"


def save_thumb(path):
    try:
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)

        os.rename(path, THUMB_FILE)
        return True
    except:
        return False


def get_thumb():
    if os.path.exists(THUMB_FILE):
        return THUMB_FILE
    return None


def clear_thumb():
    try:
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)
    except:
        pass
