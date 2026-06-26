# buttons.py (PRO CLEAN VERSION)

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_URL = "https://t.me/Anitoon_edit/33"


# =========================
# MAIN MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📁 Rename File", callback_data="rename")],
        [InlineKeyboardButton("🔄 Convert File", callback_data="convert")],
        [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
        [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])


# =========================
# BACK BUTTON
# =========================

def back_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])


# =========================
# PROCESS CONTROL BUTTONS
# =========================

def process_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{job_id}"),
            InlineKeyboardButton("▶ Resume", callback_data=f"resume_{job_id}")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{job_id}")
        ],
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)
        ]
    ])


# =========================
# THUMBNAIL SELECTION
# =========================

def thumb_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📌 Saved Thumbnail", callback_data=f"thumb_saved_{job_id}")
        ],
        [
            InlineKeyboardButton("⚡ Auto Thumbnail", callback_data=f"thumb_auto_{job_id}")
        ],
        [
            InlineKeyboardButton("❌ No Thumbnail", callback_data=f"thumb_none_{job_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back")
        ]
    ])


# =========================
# CONVERT OPTIONS
# =========================

def convert_buttons(job_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📹 Convert To Video (MP4)", callback_data=f"conv_video_{job_id}")
        ],
        [
            InlineKeyboardButton("📁 Convert To File (Document)", callback_data=f"conv_file_{job_id}")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="back")
        ]
    ])