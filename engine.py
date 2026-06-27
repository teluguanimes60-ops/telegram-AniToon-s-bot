# ==========================================================
# 🤖 AniToon Bot
# engine.py
# Part 1 / 3
# ==========================================================

import os
import shutil
import asyncio
import traceback
import time

from pyrogram.errors import FloodWait

from jobs import (
    get_job,
    update_job,
    delete_job
)

from progress import progress

from thumbnail import (
    get_thumb,
    delete_auto_thumb
)

from instant_edit import (
    save_editable_message
)

from cleaner import clean_chat

# ----------------------------------------------------------
# Supported Video Extensions
# ----------------------------------------------------------

VIDEO_EXTENSIONS = (
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v",
    ".ts",
)

# ----------------------------------------------------------
# Supported Audio Extensions
# ----------------------------------------------------------

AUDIO_EXTENSIONS = (
    ".mp3",
    ".aac",
    ".flac",
    ".wav",
    ".ogg",
    ".m4a",
)

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

def is_video(path):

    return path.lower().endswith(VIDEO_EXTENSIONS)


def is_audio(path):

    return path.lower().endswith(AUDIO_EXTENSIONS)


def safe_remove(path):

    try:

        if path and os.path.exists(path):
            os.remove(path)

    except Exception:
        pass


def safe_move(src, dst):

    try:

        shutil.move(src, dst)
        return True

    except Exception:
        return False


# ----------------------------------------------------------
# Main Pipeline
# ----------------------------------------------------------

async def process_pipeline(job_id, message, client):

    job = get_job(job_id)

    if not job:
        await message.reply_text("❌ Job not found.")
        return

    user_id = job["uid"]

    downloaded_file = None
    output_file = None
    thumb = None

    status = await message.reply_text(
        "📥 Preparing your task..."
    )

    try:

        # --------------------------------------
        # Clean old chat messages
        # --------------------------------------

        await clean_chat(user_id)

        update_job(job_id, "status", "downloading")

        start = time.time()

        downloaded_file = await message.download(
            progress=progress,
            progress_args=(
                status,
                start,
                "download"
            )
        )

        output_file = downloaded_file

        update_job(
            job_id,
            "file_path",
            downloaded_file
        )

        await status.edit_text(
            "⚙️ Processing your file..."
        )

        # Remaining processing (rename, convert,
        # thumbnail, upload, cleanup)
        # continues in Part 2.

        # ==========================================
        # RENAME MODE
        # ==========================================

        if mode == "rename":

            new_name = job.get("new_name")

            if new_name:

                ext = os.path.splitext(download_path)[1]

                final_path = os.path.join(
                    os.path.dirname(download_path),
                    new_name + ext
                )

                if os.path.exists(final_path):
                    os.remove(final_path)

                os.rename(download_path, final_path)

            else:
                final_path = download_path

        # ==========================================
        # CONVERT MODE
        # ==========================================

        elif mode == "convert":

            await status.edit_text("🎬 Converting File...")

            convert_type = job.get("convert_type", "video")

            output = os.path.splitext(download_path)[0]

            if convert_type == "video":
                final_path = output + ".mp4"

            elif convert_type == "audio":
                final_path = output + ".mp3"

            else:
                final_path = output + ".mkv"

            cmd = [
                get_ffmpeg(),
                "-y",
                "-i",
                download_path,
                final_path
            ]

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if process.returncode != 0:
                raise Exception("FFmpeg conversion failed.")

        else:

            final_path = download_path

        update_job(job_id, "status", "uploading")

        # ==========================================
        # THUMBNAIL
        # ==========================================

        thumb = await get_thumb(
            user_id=uid,
            mode=thumb_mode,
            auto_path=final_path
        )

        # ==========================================
        # CAPTION
        # ==========================================

        filename = os.path.basename(final_path)

        caption = (
            f"📁 <b>{filename}</b>\n\n"
            f"✨ Processed by AniToon Bot"
        )

        await status.edit_text(
            "📤 Uploading..."
        )

        # ==========================================
        # UPLOAD FILE
        # ==========================================

        upload_start = time.time()

        ext = os.path.splitext(final_path)[1].lower()

        video_ext = (
            ".mp4",
            ".mkv",
            ".mov",
            ".avi",
            ".webm",
            ".m4v"
        )

        audio_ext = (
            ".mp3",
            ".aac",
            ".flac",
            ".wav",
            ".ogg",
            ".m4a"
        )

        if ext in video_ext:

            await msg.reply_video(
                video=final_path,
                caption=caption,
                thumb=thumb,
                supports_streaming=True,
                progress=progress,
                progress_args=(
                    status,
                    upload_start,
                    "upload"
                )
            )

        elif ext in audio_ext:

            await msg.reply_audio(
                audio=final_path,
                caption=caption,
                progress=progress,
                progress_args=(
                    status,
                    upload_start,
                    "upload"
                )
            )

        else:

            await msg.reply_document(
                document=final_path,
                caption=caption,
                thumb=thumb,
                progress=progress,
                progress_args=(
                    status,
                    upload_start,
                    "upload"
                )
            )

        update_job(job_id, "status", "completed")

        await status.edit_text(
            "✅ File processed successfully.\n\n"
            "Thank you for using AniToon Bot ❤️"
        )

    except Exception as e:

        update_job(job_id, "status", "failed")

        print("=" * 60)
        print("ENGINE ERROR")
        print(traceback.format_exc())
        print("=" * 60)

        try:
            await status.edit_text(
                f"❌ Processing Failed\n\n{str(e)}"
            )
        except:
            pass

    finally:

        # ==========================================
        # DELETE TEMP FILES
        # ==========================================

        try:

            if download_path and os.path.exists(download_path):
                os.remove(download_path)

        except:
            pass

        try:

            if (
                final_path
                and final_path != download_path
                and os.path.exists(final_path)
            ):
                os.remove(final_path)

        except:
            pass

        try:

            if thumb and os.path.exists(thumb):
                os.remove(thumb)

        except:
            pass

        # ==========================================
        # REMOVE JOB
        # ==========================================

        delete_job(job_id)

        print(f"✅ Job {job_id} completed.")
