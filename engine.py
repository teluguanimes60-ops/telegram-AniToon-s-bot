# ==========================================
# AniToon Bot - FINAL STABLE ENGINE FIX
# ==========================================

import os
import time
import asyncio
import traceback

from queue_system import add_user, remove_user
from jobs import get_job, update_job
from progress import progress
from thumbnail import get_thumb


# ==========================================
# 🚀 PIPELINE CORE
# ==========================================
async def process_pipeline(job_id, msg, bot):

    job = get_job(job_id)
    uid = job["uid"]

    status = await msg.reply_text("📥 Starting...")

    file_path = None

    try:

        # ================= QUEUE LIMIT =================
        if not add_user(uid):
            await msg.reply_text("⛔ 20 users are processing. Please wait a few minutes and try again.")
            return

        # ================= DOWNLOAD =================
        start = time.time()

        file_path = await msg.download(
            progress=progress,
            progress_args=(status, start)
        )

        update_job(job_id, "file_path", file_path)

        await status.edit_text("⚙️ Processing file...")

        # ================= THUMBNAIL =================
        thumb_mode = job.get("thumb_mode")

        thumb = await get_thumb(
            user_id=uid,
            mode=thumb_mode,
            auto_path=file_path
        )

        # ================= RENAME =================
        if job.get("mode") == "rename":

            new_name = job.get("new_name", "AniToon_File")

            ext = os.path.splitext(file_path)[1]
            new_path = new_name + ext

            os.rename(file_path, new_path)
            file_path = new_path

        await status.edit_text("📤 Uploading...")

        caption = f"✅ {job.get('new_name','AniToon File')}"

        # ================= UPLOAD =================
        if file_path.endswith((".mp4", ".mkv", ".mov")):

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

    finally:

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

        remove_user(uid)


# ==========================================
# SAFE WRAPPER
# ==========================================
async def safe_run(job_id, msg, bot, handler):

    try:
        return await handler(job_id, msg, bot)

    except Exception:
        error_text = f"""
❌ JOB FAILED

Job ID: {job_id}

Error:
{traceback.format_exc()[:1500]}
"""
        try:
            await msg.reply_text(error_text)
        except:
            pass

    finally:
        try:
            uid = msg.from_user.id
            remove_user(uid)
        except:
            pass
