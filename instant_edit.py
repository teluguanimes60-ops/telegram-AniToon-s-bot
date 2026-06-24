# instant_edit.py

from pyrogram import Client

async def instant_edit(client, message):
    # Just re-send file quickly (no rename, no processing)
    file = message.reply_to_message

    if not file:
        await message.reply_text("⚠️ Reply to a file to use instant edit")
        return

    await message.reply_text("⚡ Instant processing...")

    path = await file.download()

    await message.reply_document(
        path,
        caption="⚡ Instant Edited File"
    )
