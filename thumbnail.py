import os

# saved thumbnail file name
THUMB_FILE = "saved_thumbnail.jpg"


# =========================
# SAVE THUMBNAIL
# =========================
def save_thumb(path):
    """
    Save a user-provided thumbnail permanently
    """

    try:
        if not path or not os.path.exists(path):
            return False

        # remove old thumb if exists
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)

        # move new thumbnail
        os.rename(path, THUMB_FILE)

        return True

    except Exception:
        return False


# =========================
# GET THUMBNAIL
# =========================
def get_thumb():
    """
    Return saved thumbnail if available
    """

    try:
        if os.path.exists(THUMB_FILE):
            return THUMB_FILE
    except:
        pass

    return None


# =========================
# DELETE THUMBNAIL (OPTIONAL SAFE RESET)
# =========================
def delete_thumb():
    """
    Remove saved thumbnail completely
    """

    try:
        if os.path.exists(THUMB_FILE):
            os.remove(THUMB_FILE)
            return True
    except:
        pass

    return False
