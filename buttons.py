# ==========================================================
# 🤖 AniToon Bot - Buttons (Project V5)
# ==========================================================

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ==========================================================
# CHANGE THESE
# ==========================================================

CHANNEL_URL = "https://t.me/Anitoon_edit/33"

# ==========================================================
# START MENU
# ==========================================================

def start_buttons(is_owner=False):

    rows = [
        [
            InlineKeyboardButton(
                "📖 Help",
                callback_data="help"
            ),
            InlineKeyboardButton(
                "ℹ️ About",
                callback_data="about"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ]
    ]

    if is_owner:
        rows.append([
            InlineKeyboardButton(
                "⚙️ Owner Settings",
                callback_data="owner_settings"
            )
        ])

    return InlineKeyboardMarkup(rows)

# ==========================================================
# FILE MENU
# ==========================================================

def file_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✏️ Rename",
                callback_data="rename"
            )
        ],

        [
            InlineKeyboardButton(
                "🎬 Convert",
                callback_data="convert"
            )
        ],

        [
            InlineKeyboardButton(
                "📝 Instant Edit",
                callback_data="instant_edit"
            )
        ],

        [
            InlineKeyboardButton(
                "📄 Media Info",
                callback_data="media_info"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel"
            )
        ]
    ])

# ==========================================================
# CONVERT MENU
# ==========================================================

def convert_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🎥 Video",
                callback_data="convert_video"
            )
        ],

        [
            InlineKeyboardButton(
                "📄 Document",
                callback_data="convert_document"
            )
        ],

        [
            InlineKeyboardButton(
                "🎵 Audio",
                callback_data="convert_audio"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_file"
            )
        ]
    ])

# ==========================================================
# VIDEO THUMBNAIL
# (NO WITHOUT THUMB)
# ==========================================================

def video_thumbnail_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🖼 Custom Thumbnail",
                callback_data="thumb_custom"
            )
        ],

        [
            InlineKeyboardButton(
                "🤖 Auto Thumbnail",
                callback_data="thumb_auto"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_convert"
            ),

            InlineKeyboardButton(
                "✅ Continue",
                callback_data="thumb_continue"
            )
        ]
    ])

# ==========================================================
# DOCUMENT THUMBNAIL
# ==========================================================

def document_thumbnail_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "🖼 Custom Thumbnail",
                callback_data="thumb_custom"
            )
        ],

        [
            InlineKeyboardButton(
                "🤖 Auto Thumbnail",
                callback_data="thumb_auto"
            )
        ],

        [
            InlineKeyboardButton(
                "🚫 Without Thumbnail",
                callback_data="thumb_none"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_convert"
            ),

            InlineKeyboardButton(
                "✅ Continue",
                callback_data="thumb_continue"
            )
        ]
    ])

# ==========================================================
# DOWNLOAD BUTTONS
# ==========================================================

def download_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⏸ Pause",
                callback_data="pause"
            ),

            InlineKeyboardButton(
                "▶ Resume",
                callback_data="resume"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_job"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ]
    ])

# ==========================================================
# UPLOAD BUTTONS
# ==========================================================

def upload_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="cancel_job"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ]
    ])

# ==========================================================
# HELP
# ==========================================================

def help_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ])

# ==========================================================
# ABOUT
# ==========================================================

def about_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📢 My Channels",
                url=CHANNEL_URL
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ])

# ==========================================================
# OWNER SETTINGS
# ==========================================================

def owner_settings_buttons():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "👥 Max Active Users",
                callback_data="set_max_users"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Channels",
                callback_data="set_channels"
            )
        ],

        [
            InlineKeyboardButton(
                "🧹 Cleaner",
                callback_data="toggle_cleaner"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ])

# ==========================================================
# SIMPLE BACK
# ==========================================================

def back_button():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="home"
            )
        ]
    ])
