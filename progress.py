import time

def progress(current, total, message, start):

    try:
        percent = (current / total) * 100 if total else 0
        elapsed = time.time() - start
        speed = current / elapsed if elapsed > 0 else 0

        bar_len = 10
        filled = int(percent / 10)

        bar = "█" * filled + "░" * (bar_len - filled)

        text = f"""
📦 Uploading...

[{bar}] {percent:.1f}%

⚡ Speed: {speed/1024/1024:.2f} MB/s
📊 {current/1024/1024:.1f}MB / {total/1024/1024:.1f}MB
"""

        try:
            message.edit_text(text)
        except:
            pass

    except:
        pass
