from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_URL = "https://t.me/Anitoon_edit/33"


def start_buttons(is_owner=False):
    rows = [
        [
            InlineKeyboardButton("✏️ Rename", callback_data="rename"),
            InlineKeyboardButton("🎬 Convert", callback_data="convert")
        ],
        [
            InlineKeyboardButton("📝 Instant Edit", callback_data="instant_edit"),
            InlineKeyboardButton("📄 Media Info", callback_data="media_info")
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)
        ]
    ]

    if is_owner:
        rows.append([
            InlineKeyboardButton(
                "⚙️ Settings",
                callback_data="settings"
            )
        ])

    return InlineKeyboardMarkup(rows)


def file_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Rename", callback_data="rename"),
            InlineKeyboardButton("🎬 Convert", callback_data="convert")
        ],
        [
            InlineKeyboardButton("📝 Instant Edit", callback_data="instant_edit"),
            InlineKeyboardButton("📄 Media Info", callback_data="media_info")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


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
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def video_thumbnail_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Custom", callback_data="thumb_custom")
        ],
        [
            InlineKeyboardButton("🤖 Auto", callback_data="thumb_auto")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
        ]
    ])


def document_thumbnail_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼 Custom", callback_data="thumb_custom")
        ],
        [
            InlineKeyboardButton("🤖 Auto", callback_data="thumb_auto")
        ],
        [
            InlineKeyboardButton("🚫 None", callback_data="thumb_none")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
        ]
    ])


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
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def upload_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_job")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def help_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def about_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def owner_settings_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Max Users", callback_data="settings_users")
        ],
        [
            InlineKeyboardButton("🧹 Cleaner", callback_data="settings_clean")
        ],
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="settings_thumb")
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])


def back_button():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅ Back", callback_data="home")
        ]
    ])
