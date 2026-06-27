# ==========================================================
# 🤖 AniToon Bot - Media Info System (Production V8)
# ==========================================================

import os
import subprocess

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# ==========================================================
# SIZE
# ==========================================================

def human_size(size):

    if not size:
        return "0 B"

    units = ("B", "KB", "MB", "GB", "TB")

    size = float(size)

    i = 0

    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1

    return f"{size:.2f} {units[i]}"

# ==========================================================
# TIME
# ==========================================================

def format_time(seconds):

    if not seconds:
        return "Unknown"

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h:02}:{m:02}:{s:02}"

    return f"{m:02}:{s:02}"

# ==========================================================
# HACHOIR
# ==========================================================

def get_media_info(path):

    info = {
        "filename": os.path.basename(path),
        "size": human_size(os.path.getsize(path)),
        "duration": "Unknown",
        "width": "-",
        "height": "-",
        "format": "-",
        "mime": "-"
    }

    try:

        parser = createParser(path)

        if parser:

            metadata = extractMetadata(parser)

            if metadata:

                if metadata.has("duration"):
                    info["duration"] = format_time(
                        metadata.get("duration").seconds
                    )

                if metadata.has("width"):
                    info["width"] = metadata.get("width")

                if metadata.has("height"):
                    info["height"] = metadata.get("height")

                if metadata.has("mime_type"):
                    info["mime"] = metadata.get("mime_type")

                if metadata.has("format"):
                    info["format"] = metadata.get("format")

            parser.close()

    except Exception:
        pass

    return info

# ==========================================================
# CODEC
# ==========================================================

def ffprobe(path):

    try:

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path
        ]

        result = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        return result if result else "Unknown"

    except Exception:
        return "Unknown"

# ==========================================================
# BUILD
# ==========================================================

def build_media_text(path):

    data = get_media_info(path)

    codec = ffprobe(path)

    return (
        "📄 <b>Media Information</b>\n\n"
        f"📁 <b>Name :</b> {data['filename']}\n"
        f"📦 <b>Size :</b> {data['size']}\n"
        f"🎞 <b>Duration :</b> {data['duration']}\n"
        f"📺 <b>Resolution :</b> {data['width']} × {data['height']}\n"
        f"🎥 <b>Codec :</b> {codec}\n"
        f"📂 <b>Format :</b> {data['format']}\n"
        f"🧾 <b>MIME :</b> {data['mime']}"
    )
