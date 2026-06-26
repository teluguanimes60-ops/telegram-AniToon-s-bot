# ==========================================
# AniToon Bot - FINAL STABILITY ENGINE (FIXED)
# ==========================================

import os
import time
import traceback

from queue_system import add_user, remove_user
from jobs import get_job, update_job
from progress import progress
from thumbnail import get_thumb

# ==========================================
# 🧠 SAFE UPLOAD WRAPPERS
# ==========================================
async def send_video(msg, file_path, caption, thumb):

    try:
        return await msg.reply_video(
            video=file_path,
            caption=caption,
            thumb=thumb if thumb else None,
            supports_streaming=True
        )
    except:
        # fallback without thumb (VERY IMPORTANT FIX)
        return await msg.reply_video(
            video=file_path,
            caption=caption,
            supports_streaming=True
        )


async def send_doc(msg, file_path, caption, thumb):

    try:
        return await msg.reply_document(
            document=file_path,
            caption=caption,
            thumb=thumb if thumb else None
        )
    except:
        return await msg.reply_document(
            document=file_path,
            caption=caption
        )

# ==========================================
# 🚀 MAIN PIPELINE
# ==========================================
async def process_pipeline(job_id, msg, bot):

    job = get_job(job_id)
    uid = job["uid"]

    status = await msg.reply_text("📥 Starting pipeline...")

    file_path = None

    try:

        # ---------------- QUEUE ----------------
        add_user(uid)

        # ---------------- DOWNLOAD ----------------
        start = time.time()

        file_path = await msg.download(
            progress=progress,
            progress_args=(status, start)
        )

        update_job(job_id, "file_path", file_path)

        await status.edit_text("⚙️ Processing file...")

        # ---------------- THUMBNAIL ----------------
        thumb = await get_thumb(
            user_id=uid,
            mode=job.get("thumb_mode"),
            auto_path=file_path
        )

        # ---------------- RENAME ----------------
        if job["mode"] == "rename":

            new_name = job.get("new_name", "file")

            ext = os.path.splitext(file_path)[1]
            new_path = new_name + ext

            os.rename(file_path, new_path)
            file_path = new_path

        await status.edit_text("📤 Uploading...")

        caption = f"✅ {job.get('new_name','AniToon File')}"

        # ---------------- UPLOAD ----------------
        if file_path.endswith((".mp4", ".mkv", ".mov")):
            await send_video(msg, file_path, caption, thumb)
        else:
            await send_doc(msg, file_path, caption, thumb)

        await status.edit_text("✅ Completed Successfully")

    except Exception as e:

        await status.edit_text("❌ Error occurred")

        print("ENGINE ERROR:", e)
        print(traceback.format_exc())

    finally:

        # ---------------- CLEANUP (ONLY ONCE) ----------------
        remove_user(uid)

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
