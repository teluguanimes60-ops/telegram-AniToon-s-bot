# ==========================================
# AniToon Bot - INSTANT EDIT (PRO FIXED)
# ==========================================

import os
import time

from jobs import update_job, get_job

# ---------------- INSTANT EDIT CORE ----------------
async def instant_edit(job_id, new_name_func):

    job = get_job(job_id)
    if not job:
        return

    msg = job.get("file")

    try:
        # ---------------- GET NEW NAME ----------------
        new_name = new_name_func()

        update_job(job_id, "new_name", new_name)

        # ---------------- FILE INFO ONLY (NO DOWNLOAD) ----------------
        file_name = getattr(msg, "document", None) or getattr(msg, "video", None)

        if file_name:
            original_name = file_name.file_name if hasattr(file_name, "file_name") else "file"

            # keep extension same
            ext = os.path.splitext(original_name)[1]

            final_name = f"{new_name}{ext}"
        else:
            final_name = new_name

        # ---------------- DIRECT RESEND ----------------
        caption = f"⚡ Instant Edit\n\n📁 {final_name}"

        # VIDEO SEND
        if getattr(msg, "video", None):

            await msg.reply_video(
                video=msg.video.file_id,
                caption=caption,
                supports_streaming=True
            )

        # DOCUMENT SEND
        elif getattr(msg, "document", None):

            await msg.reply_document(
                document=msg.document.file_id,
                caption=caption
            )

        else:

            await msg.reply_text("❌ Unsupported file type")

    except Exception as e:
        await msg.reply_text(f"❌ Instant Edit Error:\n{e}")
