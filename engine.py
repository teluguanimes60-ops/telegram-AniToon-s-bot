# ==========================================
# AniToon Bot - FINAL ENGINE (STABLE FIX)
# ==========================================

import os
import time
import traceback

from queue_system import add_user, remove_user, is_full
from jobs import get_job, update_job
from progress import progress
from thumbnail import get_thumb


# ==========================================
# 🚀 MAIN PIPELINE
# ==========================================
async def process_pipeline(job_id, msg, bot):

    job = get_job(job_id)
    uid = job["uid"]

    status = await msg.reply_text("📥 Starting pipeline...")

    file_path = None

    try:

        # ======================================
        # 🚨 QUEUE LIMIT CHECK (IMPORTANT FIX)
        # ======================================
        if is_full():
            await msg.reply_text(
                "⛔ 20 users are processing right now.\nPlease wait a few minutes and try again."
            )
            return

        # add user AFTER check
        add_user(uid)

        # ======================================
        # 📥 DOWNLOAD
        # ======================================
        start = time.time()

        file_path = await msg.download(
            progress=progress,
            progress_args=(status, start)
        )

        update_job(job_id, "file_path", file_path)

        await status.edit_text("⚙️ Processing file...")

        # ======================================
        # 🖼 THUMBNAIL
        # ======================================
        thumb_mode = job.get("thumb_mode")

        thumb = await get_thumb(
            user_id=uid,
            mode=thumb_mode,
            auto_path=file_path
        )

        # ======================================
        # ✏️ RENAME MODE
        # ======================================
        if job.get("mode") == "rename":

            new_name = job.get("new_name", "AniToon_File")

            ext = os.path.splitext(file_path)[1]
            new_path = new_name + ext

            os.rename(file_path, new_path)
            file_path = new_path

        # ======================================
        # 📤 UPLOAD
        # ======================================
        await status.edit_text("📤 Uploading...")

        caption = f"✅ {job.get('new_name','AniToon File')}"

        if file_path.endswith((".mp4", ".mkv", ".mov", ".avi")):

            await msg.reply_video(
                video=file_path,
                caption=caption,
                thumb=thumb,
                supports_streaming=True
            )

        else:

            await msg.reply_document(
                document=file_path,
                caption=caption,
                thumb=thumb
            )

        await status.edit_text("✅ Completed Successfully")

    except Exception as e:

        await status.edit_text(f"❌ Error:\n{e}")

        print("ENGINE ERROR:")
        print(traceback.format_exc())

    finally:

        # ======================================
        # 🧹 CLEANUP (VERY IMPORTANT)
        # ======================================
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        # remove user ALWAYS
        remove_user(uid)
