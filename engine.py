# ==========================================================
# 🤖 AniToon Bot
# ==========================================================

import os
import time
import shutil
import traceback
import subprocess

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

from media_info import build_media_text


# ==========================================================
# FILE TYPES
# ==========================================================

VIDEO_EXTENSIONS = (
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v",
    ".ts",
    ".flv"
)

AUDIO_EXTENSIONS = (
    ".mp3",
    ".aac",
    ".wav",
    ".ogg",
    ".flac",
    ".m4a"
)


# ==========================================================
# SAFE DELETE
# ==========================================================

def safe_delete(path):

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ==========================================================
# CONVERTER
# ==========================================================

def convert_file(input_file, mode):

    root = os.path.splitext(input_file)[0]

    if mode == "video":

        output = root + ".mp4"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output
        ]

    elif mode == "audio":

        output = root + ".mp3"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            output
        ]

    elif mode == "document":

        return input_file

    else:

        return input_file

    try:

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        if os.path.exists(output):
            return output

    except Exception:
        pass

    return input_file


# ==========================================================
# MAIN PIPELINE
# ==========================================================

async def process_pipeline(job_id, message, bot):

    job = get_job(job_id)

    if not job:

        await message.reply_text(
            "❌ Job not found."
        )

        return

    uid = job["uid"]

    status = await message.reply_text(
        "📥 Starting..."
    )

    file_path = None
    thumb = None
    auto_thumb = False

    try:

        # ==========================================
        # DOWNLOAD
        # ==========================================

        update_job(job_id, "status", "downloading")

        start = time.time()

        file_path = await message.download(
            progress=progress,
            progress_args=(
                status,
                start,
                "download"
            )
        )

        update_job(
            job_id,
            "file_path",
            file_path
        )

        await status.edit_text(
            "⚙ Processing..."
        )

        # ==========================================
        # MEDIA INFO MODE
        # ==========================================

        if job.get("mode") == "media_info":

            text = build_media_text(file_path)

            await message.reply_text(text)

            safe_delete(file_path)

            delete_job(job_id)

            return

        # ==========================================
        # CONVERT
        # ==========================================

        convert_mode = job.get("convert_type") or job.get("convert_mode")

        if convert_mode:

            converted = convert_file(
                file_path,
                convert_mode
            )

            if converted != file_path:
                safe_delete(file_path)

            file_path = converted

            update_job(
                job_id,
                "file_path",
                file_path
            )

        # ==========================================
        # RENAME
        # ==========================================

        if job.get("new_name"):

            ext = os.path.splitext(file_path)[1]

            new_path = job["new_name"] + ext

            shutil.move(
                file_path,
                new_path
            )

            file_path = new_path

            update_job(
                job_id,
                "file_path",
                file_path
            )

        # ==========================================
        # THUMBNAIL
        # ==========================================

        thumb = await get_thumb(
            client=bot,
            user_id=uid,
            mode=job.get(
                "thumb_mode",
                "auto"
            ),
            auto_path=file_path
        )

        if (
            job.get("thumb_mode") == "auto"
            and thumb
        ):
            auto_thumb = True

                    # ==========================================
        # UPLOADING
        # ==========================================

        update_job(
            job_id,
            "status",
            "uploading"
        )

        await status.edit_text(
            "📤 Uploading..."
        )

        start = time.time()

        caption = os.path.basename(file_path)

        is_video = file_path.lower().endswith(VIDEO_EXTENSIONS)
        is_audio = file_path.lower().endswith(AUDIO_EXTENSIONS)

        if is_video:

            await message.reply_video(
                video=file_path,
                caption=caption,
                thumb=thumb,
                supports_streaming=True,
                progress=progress,
                progress_args=(
                    status,
                    start,
                    "upload"
                )
            )

        elif is_audio:

            await message.reply_audio(
                audio=file_path,
                caption=caption,
                progress=progress,
                progress_args=(
                    status,
                    start,
                    "upload"
                )
            )

        else:

            if job.get("thumb_mode") == "none":
                thumb = None

            await message.reply_document(
                document=file_path,
                caption=caption,
                thumb=thumb,
                progress=progress,
                progress_args=(
                    status,
                    start,
                    "upload"
                )
            )

        # ==========================================
        # FINISHED
        # ==========================================

        update_job(
            job_id,
            "status",
            "completed"
        )

        try:

            await status.edit_text(
                "✅ File processed successfully."
            )

        except:
            pass

    except Exception as e:

        print("=" * 60)
        print("ENGINE ERROR")
        print(traceback.format_exc())
        print("=" * 60)

        update_job(
            job_id,
            "status",
            "failed"
        )

        try:

            await status.edit_text(
                f"❌ Processing Failed\n\n{e}"
            )
        except:
            pass

    finally:

        # ------------------------------------------
        # Delete processed file
        # ------------------------------------------

        safe_delete(file_path)

        # ------------------------------------------
        # Delete only AUTO thumbnail
        # Custom thumbnails downloaded from Telegram
        # are temporary files, so delete them normally.
        # ------------------------------------------

        if thumb:

            if auto_thumb:
                delete_auto_thumb(thumb)
            else:
                safe_delete(thumb)

        # ------------------------------------------
        # Remove Job
        # ------------------------------------------

        delete_job(job_id)
