# ===========================
# AniToon Bot - INSTANT EDIT (FIXED)
# ===========================

import os


async def instant_edit(client, message, new_name):
    """
    Instant rename without processing UI.
    Keeps file type same (video/document/audio).
    """

    try:
        file_msg = message.reply_to_message

        if not file_msg:
            await message.reply_text("⚠️ Reply to a file/video to use instant edit")
            return

        # download file quickly
        path = await file_msg.download()

        # detect extension
        ext = os.path.splitext(path)[1]

        # create new name
        if "." in new_name:
            new_path = new_name
        else:
            new_path = new_name + ext

        # rename file locally
        os.rename(path, new_path)

        caption = f"⚡ Instant Edited: {new_name}"

        # send same type back
        if file_msg.video:
            await message.reply_video(
                video=new_path,
                caption=caption
            )

        elif file_msg.document:
            await message.reply_document(
                document=new_path,
                caption=caption
            )

        elif file_msg.audio:
            await message.reply_audio(
                audio=new_path,
                caption=caption
            )

        else:
            await message.reply_document(
                document=new_path,
                caption=caption
            )

        # cleanup
        try:
            os.remove(new_path)
        except:
            pass

    except Exception as e:
        await message.reply_text(f"❌ Instant Edit Error:\n{e}")
