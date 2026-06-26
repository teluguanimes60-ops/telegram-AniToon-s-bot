# ==========================================================
# 🤖 AniToon's Bot - Production Buttons v2
# ==========================================================

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================================
# CHANGE THIS
# ==========================================================

CHANNEL_URL = "https://t.me/YOUR_CHANNEL"

# ==========================================================
# 🏠 START MENU
# ==========================================================

def start_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("📢 My Channels", url=CHANNEL_URL)
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ])


# ==========================================================
# 📂 FILE MENU
# ==========================================================

def file_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Rename", callback_data="rename")
        ],
        [
            InlineKeyboardButton("🎬 Convert", callback_data="convert")
        ],
        [
            InlineKeyboardButton("📝 Instant Edit", callback_data="instant_edit")
        ],
        [
            InlineKeyboardButton("📄 Media Info", callback_data="media_info")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ])


# ==========================================================
# 🎬 CONVERT MENU
# ==========================================================

def convert_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎥 Video", callback_data="convert_video")
        ],
        [
            InlineKeyboardButton("📄 Document", callback_data="convert_document")
        ],
        [
            InlineKeyboardButton("🎵 Audio", callback_data="convert_audio")
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back_file")
        ]
    ])


# ==========================================================
# 🖼 THUMBNAIL MENU
# ==========================================================

def thumbnail_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Custom Thumbnail", callback_data="thumb_custom")
        ],
        [
            InlineKeyboardButton("🤖 Auto Thumbnail", callback_data="thumb_auto")
        ],
        [
            InlineKeyboardButton("🚫 Without Thumbnail", callback_data="thumb_none")
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back_convert"),
            InlineKeyboardButton("✅ Continue", callback_data="thumb_continue")
        ]
    ])


# ==========================================================
# ⬇ DOWNLOAD BUTTONS
# ==========================================================

def download_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("▶ Resume", callback_data="resume")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
        ],
        [
            InlineKeyboardButton("📢 My Channels", url=CHANNEL_URL)
        ]
    ])


# ==========================================================
# ⬆ UPLOAD BUTTONS
# ==========================================================

def upload_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
        ],
        [
            InlineKeyboardButton("📢 My Channels", url=CHANNEL_URL)
        ]
    ])


# ==========================================================
# ⚙ SETTINGS
# ==========================================================

def settings_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="settings_thumb")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner", callback_data="settings_clean")
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home")
        ]
    ])


# ==========================================================
# 📖 HELP
# ==========================================================

def help_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home")
        ]
    ])


# ==========================================================
# ℹ ABOUT
# ==========================================================

def about_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 My Channels", url=CHANNEL_URL)
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home")
        ]
    ])


# ==========================================================
# SIMPLE BACK
# ==========================================================

def back_button():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home")
        ]
    ])
