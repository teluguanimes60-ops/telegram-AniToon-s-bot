from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_URL = "https://t.me/Anitoon_edit/33"

# =========================
# MAIN MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📁 Rename", callback_data="rename")],
            [InlineKeyboardButton("🔄 Convert", callback_data="convert")],
            [InlineKeyboardButton("⚡ Instant Edit", callback_data="instant")],
            [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb")],
            [InlineKeyboardButton("ℹ Help", callback_data="help")]
        ]
    )


# =========================
# BACK BUTTON
# =========================

def back_btn():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ]
    )


# =========================
# THUMBNAIL SELECTION
# =========================

def thumb_buttons(job_id):
    return InlineKeyboardMarkup(
        [
           
