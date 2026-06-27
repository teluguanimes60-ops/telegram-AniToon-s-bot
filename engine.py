# ==========================================================
# 🤖 AniToon Bot - Processing Engine v4
# Stable | Queue Compatible | Production Ready
# ==========================================================

import os
import time
import traceback

from jobs import (
    get_job,
    update_job,
    delete_job
)

from progress import progress
from thumbnail import get_thumb


# ==========================================================
# MAIN PIPELINE
# ==========================================================

async def process_pipeline(job_id, msg, bot):

    job = get_job(job_id)

    if job is None:
        await msg.reply_text("❌ Job not found.")
        return

    uid = job["uid"]

    status = await msg.reply_text("📥 Starting pipeline...")

    file_path = None
    thumb = None

    try:

        update_job(job_id, "status", "downloading")

        start = time.time()

        file_path = await msg.download(
            progress=progress,
            progress_args=(status, start)
        )

        update_job(job_id, "file_path", file_path)

        await status.edit_text("⚙️ Processing...")

        # ==================================================
        # THUMBNAIL
        # ==================================================

        thumb = await get_thumb(
            user_id=uid,
            mode=job.get("thumb_mode", "auto"),
            auto_path=file_path
        )

        # ==================================================
        # RENAME
        # ==================================================

        if job.get("mode") == "rename":

            new_name = job.get("new_name")

            if new_name:

                ext = os.path.splitext(file_path)[1]

                new_path = new_name + ext

                os.rename(file_path, new_path)

                file_path = new_path

                update_job(job_id, "file_path", file_path)

        update_job(job_id, "status", "uploading")

        await status.edit_text("📤 Uploading...")

        caption = f"✅ {os.path.basename(file_path)}"

        if file_path.lower().endswith(
            (
                ".mp4",
                ".mkv",
                ".mov",
                ".avi",
                ".webm",
                ".m4v"
            )
        ):

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

        update_job(job_id, "status", "completed")

        await status.edit_text(
            "✅ File processed successfully."
        )

    except Exception as e:

        update_job(job_id, "status", "failed")

        print("=" * 60)
        print("ENGINE ERROR")
        print(traceback.format_exc())
        print("=" * 60)

        await status.edit_text(
            f"❌ Processing Failed\n\n{e}"
        )

    finally:

        try:

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

        except Exception:
            pass

        try:

            if thumb and os.path.exists(thumb):
                os.remove(thumb)

        except Exception:
            pass

        delete_job(job_id)
