from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_URL = "https://t.me/Anitoon_edit/33"

# Main Menu
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert File", callback_data="convert")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])


# Back Button
def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])


# Processing Buttons
def process_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⏸ Pause",
                callback_data=f"pause_{job_id}"
            ),
            InlineKeyboardButton(
                "▶ Resume",
                callback_data=f"resume_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data=f"cancel_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url=CHANNEL_URL
            )
        ]
    ])


# Thumbnail Selection
def thumb_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📌 Saved Thumb",
                callback_data=f"thumb_saved_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ Auto Thumb",
                callback_data=f"thumb_auto_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No Thumb",
                callback_data=f"thumb_none_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url=CHANNEL_URL
            )
        ]
    ])


# Convert Type Buttons
def convert_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📹 Video",
                callback_data=f"conv_video_{job_id}"
            ),
            InlineKeyboardButton(
                "📁 File",
                callback_data=f"conv_file_{job_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url=CHANNEL_URL
            )
        ]
    ])
