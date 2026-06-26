# ==========================================================
# 🤖 AniToon's Bot - Production Buttons
# ==========================================================

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================================================
# 🏠 START MENU
# ==========================================================

def start_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 Help", callback_data="help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/YOUR_CHANNEL")
            ],
            [
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ]
        ]
    )


# ==========================================================
# 📂 FILE MENU
# ==========================================================

def file_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏️ Rename", callback_data="rename")
            ],
            [
                InlineKeyboardButton("🎬 Convert", callback_data="convert")
            ],
            [
                InlineKeyboardButton("📝 Instant Caption", callback_data="instant")
            ],
            [
                InlineKeyboardButton("📊 Media Info", callback_data="mediainfo")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel")
            ]
        ]
    )


# ==========================================================
# 🎬 CONVERT MENU
# ==========================================================

def convert_buttons():
    return InlineKeyboardMarkup(
        [
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
        ]
    )


# ==========================================================
# 🖼 VIDEO THUMBNAIL MENU
# (Shown ONLY for Rename Video / Convert to Video)
# ==========================================================

def thumbnail_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖼 Custom Thumbnail", callback_data="thumb_custom")
            ],
            [
                InlineKeyboardButton("🤖 Auto Thumbnail", callback_data="thumb_auto")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_convert")
            ],
            [
                InlineKeyboardButton("✅ Continue", callback_data="thumb_continue")
            ]
        ]
    )


# ==========================================================
# ⚙️ SETTINGS
# ==========================================================

def settings_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🖼 Thumbnail", callback_data="settings_thumb")
            ],
            [
                InlineKeyboardButton("🧹 Auto Clean", callback_data="settings_clean")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="home")
            ]
        ]
    )


# ==========================================================
# 📤 PROGRESS BUTTONS
# ==========================================================

def progress_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("▶ Resume", callback_data="resume")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
            ]
        ]
    )


# ==========================================================
# 🔙 SIMPLE BACK BUTTON
# ==========================================================

def back_button():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="home")
            ]
        ]
    )
